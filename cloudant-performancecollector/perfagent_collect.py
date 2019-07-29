import base64
import bz2
import gzip
import logging
import datetime
import time
import subprocess
import select
import re
import os.path
from collections import Counter
import pandas as pd
import numpy as np
import json
import requests
from data_collect import *

def get_groupcriteria(granularity,scope):
      groupcriteria = ['mtime','mtime_epoch']
      if granularity == 'all':
       groupcriteria = ['mtime','mtime_epoch'] 
       if scope == 'endpoint' :
         groupcriteria = ['cluster','loghost','database','verb','endpoint']
       elif scope == 'verb' :
         groupcriteria = ['cluster','loghost','database','verb']
       elif scope == 'database' :
         groupcriteria = ['cluster','loghost','database']
      else:
       if scope == 'endpoint' :
         groupcriteria = ['cluster','loghost','database','verb','endpoint','mtime','mtime_epoch']
       elif scope == 'verb' :
         groupcriteria = ['cluster','loghost','database','verb','mtime','mtime_epoch']
       elif scope == 'database' :
         groupcriteria = ['cluster','loghost','database','mtime','mtime_epoch']
       elif scope == 'all':
         groupcriteria = ['cluster','loghost','mtime','mtime_epoch']
      return groupcriteria


def test_conditions(row,conditions):
    event_found = False
    events = []
    for c in conditions:
      thisValue = getattr(row,c[0])
      thisQualifierValue = getattr(row,c[3])
      # condition holds the threshold in c0-c2 and the qualifier in c3-5
      if test_condition(c[1],int(c[2]),thisValue) and test_condition(c[4],int(c[5]),thisQualifierValue):
       events.append('AlertKey=Threshold Breach,Condition=['+str(c[0])+str(c[1])+str(c[2])+'],Value=['+str(thisValue)+\
                      '],Qualifier=['+str(c[3])+str(c[4])+str(c[5])+'],QValue=['+str(thisQualifierValue)+']')
       event_found = True
    return event_found,events

def find_threshold_events(row,thresholds,exclusions):
    event_found = False
    events = []
    database = '.'
    verb = '.'
    endpoint = '.'
    try:
     database = getattr(row,'database')
    except:
     pass
    try:
     verb = getattr(row,'verb')
    except:
     pass
    try:
     endpoint = getattr(row,'endpoint')
    except:
     pass
    if not exclude_entry(database,verb,endpoint,exclusions):
     key_result,conditions = match_resourcekey(database,verb,endpoint,thresholds)
     if key_result:
      event_found,events = test_conditions(row,conditions)
    return event_found,events

def generate_events_output(op,thresholds,exclusions,granularity,scope,fromtime,totime,location,id,format):
    if os.path.exists(location):
      ofile = location + '/events_' + scope + '_by_' + granularity + '_' + fromtime + '_to_' + totime + '_' + id +'.csv'
      oevents = []
      event_counter = 0
      if len(op.index) > 0:
       if format == 'csv':
        ef = open(ofile,'w')
       for row in op.itertuples():
          resource_key = get_resource_key(row,scope)
          time_key = getattr(row,'mtime')
          epoch_key = getattr(row,'mtime_epoch') 
          event_found,events = find_threshold_events(row,thresholds,exclusions)
          if event_found:
            event_counter = event_counter+1
            for e in events:
             if format == 'csv':
              opstring = resource_key+',EventTime='+time_key+',EventEpoch='+str(epoch_key)+','+str(e)+'\n' 
              ef.write(opstring)
              ef.flush()
             if format == 'json':
               oevents.append({'resource':resource_key,'eventtime':time_key, 'eventepoch':epoch_key, 'eventdetails':e})
       if format == 'csv':
        ef.close() 
      logging.warn("{cloudant performance agent} Request Processing for id ["+str(id)+"] Event Lines Generated = ["+str(event_counter)+"]")
      return oevents,event_counter
    else:
      logging.warn('{cloudant performance agent} Results location not found <' + str(location) + '>')

def generate_stats_output(op,granularity,scope,fromtime,totime,location,id,format):
    if os.path.exists(location):
      ofile = location + '/stats_' + scope + '_by_' + granularity + '_' + fromtime + '_to_' + totime + '_' + id + '.csv'
      columns=['mtime','mtime_epoch','tqmin','tqavg','tqmax','tqcount','tqsum',\
               'tcmin','tcavg','tcmax','tccount','tcsum',\
               'trmin','travg','trmax','trcount','trsum',\
               'ttmin','ttavg','ttmax','ttcount','ttsum','ttrmin','ttravg','ttrmax','ttrcount','ttrsum',\
               'szmin','szavg','szmax','szcount','szsum',\
               'femin','feavg','femax','fecount','fesum',\
               'bemin','beavg','bemax','becount','besum',\
               'st2count','st3count','st4count','st5count','stfailpct'] 
      if scope == 'all':
       columns = ['cluster','loghost'] + columns
      elif scope == 'database':
       columns = ['cluster','loghost','database'] + columns
      elif scope == 'verb':
       columns = ['cluster','loghost','database','verb'] + columns
      elif scope == 'endpoint':
       columns = ['cluster','loghost','database','verb','endpoint'] + columns
      if format == 'csv':
       op.to_csv(ofile,columns=columns)
       logging.warn("{cloudant performance agent} Request Processing for id ["+str(id)+"] Stats Lines Generated = ["+str(len(op.index))+"]")
       return None,len(op.index)
      if format == 'json':
       opjson = op.to_json(orient='records')
       logging.warn("{cloudant performance agent} Request Processing for id ["+str(id)+"] Stats Lines Generated = ["+str(len(op.index))+"]")
       return opjson,len(op.index)
    else:
      logging.warn('{cloudant performance agent} Results location not found <' + str(location) + '>')


def execute_collect(scope,s_url,s_credentials,s_username,s_password,p_url,certverif,inputlogfile,thresholdsfile,\
       eventsexclusionsfile,statsexclusionsfile,fromtime,totime,granularity,performercount,resultslocation,resultsid,outputformat,loghost,cluster_url):
   try:   
      logging.warn("{cloudant performance agent} Request Processing for id ["+str(resultsid)+"] time-boundary ["+str(fromtime)+"-"+str(totime)+"] Start")
      result_stats = []
      event_stats = [] 
      numstats = 0
      basestats = find_dbstats(inputlogfile,fromtime,totime,granularity,read_exclusions(statsexclusionsfile),loghost,cluster_url)
      if basestats is None:
         logging.warn("{cloudant performance agent} Request Processing for id ["+str(resultsid)+"] Log Lines Found = [0]")
         result_stats = []
         result_events = [] 
      else:
        numloglines = len(basestats.index)
        logging.warn("{cloudant performance agent} Request Processing for id ["+str(resultsid)+"] Log Lines Found = ["+str(numloglines)+"]")
        if numloglines == 0:
         result_stats = []
         result_events = [] 
        else: 
         groupedstats = get_groups(basestats,get_groupcriteria(granularity,scope))
         logging.warn("{cloudant performance agent} Request Processing for id ["+str(resultsid)+"] Resource Groups Found = ["+str(len(groupedstats))+"]")
         ostats,numstats = generate_stats_output(groupedstats,granularity,scope,fromtime,totime,resultslocation,resultsid,outputformat)
         oevents,numevents = generate_events_output(groupedstats,read_thresholds(thresholdsfile),read_exclusions(eventsexclusionsfile),granularity,scope,\
           fromtime,totime,resultslocation,resultsid,outputformat)
         if outputformat == 'json':
          if numstats > 0:
            result_stats = json.loads(ostats)
          else:
            result_stats = []
          if numevents > 0:
            result_events = oevents
          else:
            result_events = []
      if outputformat == 'json':
       result =  { "stats" : result_stats,  "events" : result_events}
      else:
       if numstats == 0:
         result = { "statsfile" : "", "eventsfile" : "" }
       else: 
         result = { "statsfile" : str(resultslocation)+ '/stats_'+scope+'_by_'+granularity+'_'+fromtime+'_to_'+totime+'_'+str(resultsid)+'.csv', 
       "eventsfile" : str(resultslocation)+ '/events_'+scope+'_by_'+granularity+'_'+fromtime+'_to_'+totime+'_'+str(resultsid)+'.csv' }
      logging.warn("{cloudant performance agent} Request Processing for id ["+str(resultsid)+"] End")
      return result 
   except Exception as e:
      logging.warn("{cloudant performance agent} Request Processing Unexpected  Error : "+str(e))
      logging.warn("{cloudant performance agent} Request Processing for id ["+str(resultsid)+"] End")
      return None
