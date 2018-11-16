import base64
import bz2
import gzip
import string
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
from perfagent_menu import *
from data_collect import *
from api_utils import *

def get_body_groupcriteria(granularity,scope):
      
      groupcriteria = ['mtime','mtime_epoch']
      if granularity == 'all':
       groupcriteria = ['mtime','mtime_epoch'] 
       if scope == 'body' :
         groupcriteria = ['cluster','loghost','client','database','verb','endpoint','body']
       elif scope == 'endpoint' :
         groupcriteria = ['cluster','loghost','client','database','verb','endpoint']
       elif scope == 'verb' :
         groupcriteria = ['cluster','loghost','client','database','verb']
       elif scope == 'database' :
         groupcriteria = ['cluster','loghost','client']
      else:
       if scope == 'body' :
         groupcriteria = ['cluster','loghost','client','database','verb','endpoint','body','mtime','mtime_epoch']
       elif scope == 'endpoint' :
         groupcriteria = ['cluster','loghost','client','database','verb','endpoint','mtime','mtime_epoch']
       elif scope == 'verb' :
         groupcriteria = ['cluster','loghost','client','database','verb','mtime','mtime_epoch']
       elif scope == 'database' :
         groupcriteria = ['cluster','loghost','client','mtime','mtime_epoch']
       elif scope == 'all':
         groupcriteria = ['cluster','loghost','mtime','mtime_epoch']
      return groupcriteria


def generate_body_stats_output(op,granularity,scope,fromtime,totime,location,id,format):
    if os.path.exists(location):
      ofile = location + '/bodystats_' + scope + '_by_' + granularity + '_' + fromtime + '_to_' + totime + '_' + id + '.csv'
      columns=['mtime','mtime_epoch','tqmin','tqavg','tqmax','tqcount','tqsum','trmin','travg','trmax','trcount','trsum',\
               'ttmin','ttavg','ttmax','ttcount','ttsum','ttrmin','ttravg','ttrmax','ttrcount','ttrsum',\
               'szmin','szavg','szmax','szcount','szsum','st2count','st3count','st4count','st5count','stfailpct'] 
      if scope == 'all':
       columns = ['cluster','loghost'] + columns
      elif scope == 'client':
       columns = ['cluster','loghost','client'] + columns
      elif scope == 'verb':
       columns = ['cluster','loghost','client','database','verb'] + columns
      elif scope == 'endpoint':
       columns = ['cluster','loghost','client','database','verb','endpoint'] + columns
      elif scope == 'body':
       columns = ['cluster','loghost','client','database','verb','endpoint','body'] + columns
      if format == 'csv':
       op.to_csv(ofile,columns=columns)
       logging.warn("{cloudant body data collector} Request Processing for id ["+str(id)+"] Stats Lines Generated = ["+str(len(op.index))+"]")
       return None,len(op.index)
      if format == 'json':
       opjson = op.to_json(orient='records')
       logging.warn("{cloudant body data collector} Request Processing for id ["+str(id)+"] Stats Lines Generated = ["+str(len(op.index))+"]")
       return opjson,len(op.index)
    else:
      logging.warn('{cloudant body data collector} Results location not found <' + str(location) + '>')


def execute_body_collect(scope,s_url,s_credentials,s_username,s_password,p_url,certverif,inputlogfile,thresholdsfile,\
       eventsexclusionsfile,statsexclusionsfile,fromtime,totime,granularity,performercount,resultslocation,resultsid,outputformat,loghost,cluster_url):
   try:   
      logging.warn("{cloudant body data collector} Request Processing for id ["+str(resultsid)+"] time-boundary ["+str(fromtime)+"-"+str(totime)+"] Start")
      result_stats = []
      event_stats = [] 
      numstats = 0
      basestats = find_dbstats(inputlogfile,fromtime,totime,granularity,read_exclusions(statsexclusionsfile),loghost,cluster_url)
      if basestats is None:
         logging.warn("{cloudant body data collector} Request Processing for id ["+str(resultsid)+"] Log Lines Found = [0]")
         result_stats = []
         result_events = [] 
      else:
        numloglines = len(basestats.index)
        logging.warn("{cloudant body data collector} Request Processing for id ["+str(resultsid)+"] Log Lines Found = ["+str(numloglines)+"]")
        if numloglines == 0:
         result_stats = []
         result_events = [] 
        else: 
         groupedstats = get_groups(basestats,get_body_groupcriteria(granularity,scope))
         logging.warn("{cloudant body data collector} Request Processing for id ["+str(resultsid)+"] Resource Groups Found = ["+str(len(groupedstats))+"]")
         ostats,numstats = generate_body_stats_output(groupedstats,granularity,scope,fromtime,totime,resultslocation,resultsid,outputformat)
         if outputformat == 'json':
          if numstats > 0:
            result_stats = json.loads(ostats)
          else:
            result_stats = []
      if outputformat == 'json':
       result =  { "stats" : result_stats,  "events" : result_events}
      else:
       if numstats == 0:
         result = { "statsfile" : "", "eventsfile" : "" }
       else: 
         result = { "statsfile" : str(resultslocation)+ '/stats_'+scope+'_by_'+granularity+'_'+fromtime+'_to_'+totime+'_'+str(resultsid)+'.csv', 
       "eventsfile" : str(resultslocation)+ '/events_'+scope+'_by_'+granularity+'_'+fromtime+'_to_'+totime+'_'+str(resultsid)+'.csv' }
      logging.warn("{cloudant body data collector} Request Processing for id ["+str(resultsid)+"] End")
      return result 
   except Exception as e:
      logging.warn("{cloudant body data collector} Request Processing Unexpected  Error : "+str(e))
      logging.warn("{cloudant body data collector} Request Processing for id ["+str(resultsid)+"] End")
      return None


try:    
  requests.urllib3.disable_warnings()
except:
  try:
    requests.packages.urllib3.disable_warnings()
  except:
    logging.warn("{cloudant body data collector} Unable to disable urllib3 warnings")
    pass

defaults_file = "/opt/cloudant-performancecollector/perfagent.conf"
logfilename = "/var/log/cloudant_bodydata_collector.log"

logging.basicConfig(filename = logfilename, level=logging.WARN,
                    format='%(asctime)s[%(funcName)-5s] (%(processName)-10s) %(message)s',
                    )

if __name__ == "__main__":
    opts, args = options()
    valid_selection = False
    
    default_connectioninfo, default_certificate_verification,default_requests_ca_bundle,default_inputlogfile,default_thresholdsfile,\
     default_eventsexclusionsfile,default_statsexclusionsfile,default_scope,default_granularity,\
     default_performercount, default_resultslocation, default_outputformat = process_defaults_config(defaults_file)
    
    if default_certificate_verification == 'True':
       opts.certverif = True
       if os.path.exists(default_requests_ca_bundle):
          os.environ['REQUESTS_CA_BUNDLE'] = default_requests_ca_bundle
       else:
          print("REQUESTS_CA_BUNDLE file ["+str(default_requests_ca_bundle)+"] does not exist - all sessions will fail")
          logging.warn("REQUESTS_CA_BUNDLE file ["+str(default_requests_ca_bundle)+"] does not exist - all sessions will fail")
    else:
       opts.certverif = False

    if not opts.inputlogfile:
       opts.inputlogfile = default_inputlogfile

    if not opts.thresholdsfile:
       opts.thresholdsfile = default_thresholdsfile

    if not opts.eventsexclusionsfile:
       opts.eventsexclusionsfile = default_eventsexclusionsfile

    if not opts.statsexclusionsfile:
       opts.statsexclusionsfile = '/opt/cloudant-performancecollector/bodydata_stats_exclusions.info'

    if not opts.scope:
       opts.scope = default_scope
       valid_scope = True
    elif opts.scope == 'client'  or  opts.scope == 'endpoint'  or opts.scope == 'verb' or opts.scope == 'all':
       valid_scope = True
    else:
       valid_scope = False
 
    if not opts.granularity:
       opts.granularity = default_granularity
       valid_granularity = True
    elif opts.granularity == 'second' or opts.granularity == 'minute'  or  opts.granularity == 'hour'  or opts.granularity == 'day' or opts.granularity == 'all':
       valid_granularity = True
    else:
       valid_granularity = False
 
    if not opts.performercount:
       opts.performercount = default_performercount

    if not opts.resultslocation:
       opts.resultslocation = default_resultslocation

    if not opts.outputformat:
       opts.outputformat = default_outputformat

    if not opts.logfilehost:
       opts.logfilehost = ''

    if not opts.connectioninfo:
       opts.connectioninfo = default_connectioninfo 
    
    s_url,s_credentials,s_username,s_password,p_url = process_connection_info(opts.connectioninfo)

    if s_url is None or s_credentials is None or s_username is None or s_password is None: 
          print("bodycollector: Cannot process connection info [" + str(opts.connectioninfo) + "]")
          sys.exit(1)
         
    if opts.scope and valid_granularity:
          opts.fromtime,opts.totime = process_timeperiod(opts.fromtime,opts.totime) 
          if len(opts.fromtime) == 12 and len(opts.totime) == 12:
              resultsid = datetime.datetime.now().strftime("%Y%m%d%H%M%f")
              execute_body_collect(opts.scope,s_url,s_credentials,s_username,s_password,p_url,opts.certverif,\
               opts.inputlogfile,opts.thresholdsfile,opts.eventsexclusionsfile,opts.statsexclusionsfile,\
               opts.fromtime,opts.totime,opts.granularity,opts.performercount,opts.resultslocation,resultsid,opts.outputformat,opts.logfilehost,s_url)
              valid_selection = True
    
    if not valid_selection:
       print "bodycollector: Command not recognised"
