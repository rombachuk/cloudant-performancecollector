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

def test_field(searchlist,index,field,value):
      if field in searchlist[index]:
        result = re.search(searchlist[index][field],value)
        if result != None:
         if len(result.group(0)) > 0:
           return True
         else:
           return False
        else:
          return False
      else:
        return True # assume exclude if not in list 

def exclude_client(clientip,exclusions):
    exclude = False
    index = 0
    while not exclude and index < len(exclusions):
     if 'clientip' in exclusions[index]:
        result = re.search(exclusions[index]['clientip'],clientip)
        if result != None:
         if len(result.group(0)) > 0:
           exclude = True
     index = index + 1
    return exclude

def exclude_entry(database,verb,endpoint,exclusions):
    exclude = False
    index = 0
    while not exclude and index < len(exclusions):
     if not 'clientip' in exclusions[index]:
      if test_field(exclusions,index,'database',database):
       if test_field(exclusions,index,'verb',verb):
        if test_field(exclusions,index,'endpoint',endpoint): 
          exclude = True
     index = index + 1
    return exclude

def process_collectconfig(cfile):
    linetime_format = '%d/%b/%Y:%H:%M'
    linetime_index = int(6) 
    linetime_start = int(1)
    linetime_end = int(-8)
    timings_index = int(9)
    status_index = int(10)
    size_index = int(11)
    base_index = int(19)
    if cfile and os.path.isfile(cfile):
      cf = open(cfile,'r')
      cflines = cf.readlines()
      for cfline in cflines:
          cflineparts = cfline.split()
          if len(cflineparts) == 2 and cflineparts[0] == 'linetime_format':
            linetime_format = str(cflineparts[1])
          elif len(cflineparts) == 2 and cflineparts[0] == 'linetime_index':
            linetime_index = int(cflineparts[1])
          elif len(cflineparts) == 2 and cflineparts[0] == 'linetime_start':
            linetime_start = int(cflineparts[1])
          elif len(cflineparts) == 2 and cflineparts[0] == 'linetime_end':
            linetime_end = int(cflineparts[1])
          elif len(cflineparts) == 2 and cflineparts[0] == 'timings_index':
            timings_index = int(cflineparts[1])
          elif len(cflineparts) == 2 and cflineparts[0] == 'status_index':
            status_index = int(cflineparts[1])
          elif len(cflineparts) == 2 and cflineparts[0] == 'size_index':
            size_index = int(cflineparts[1])
          elif len(cflineparts) == 2 and cflineparts[0] == 'base_index':
            base_index = int(cflineparts[1])
          else:
            pass
      cf.close()
    return linetime_format,linetime_index,linetime_start,linetime_end, timings_index,status_index,size_index,base_index

def process_dbstatline(thisline,fromtime,totime,thislist,granularity,exclusions,loghost,clusterurl,\
        linetime_format,linetime_index,linetime_start,linetime_end, timings_index,status_index,size_index,base_index): 
    database='unknown'
    verb='unknown'
    endpoint='unknown'
    params=None
    lineparts = thisline.split()
    if len(lineparts) > 6 and 'haproxy' in thisline:
     try:
        linetime = datetime.datetime.strptime(lineparts[linetime_index][linetime_start:linetime_end],linetime_format).strftime('%Y%m%d%H%M')
        if linetime < fromtime or linetime >= totime:
         return linetime
        if granularity == 'minute':   
         markertime = linetime 
         markertime_epoch = int(time.mktime(time.strptime(markertime, "%Y%m%d%H%M"))) 
        elif granularity == 'hour':   
         markertime = linetime[0:-2] 
         markertime_epoch = int(time.mktime(time.strptime(markertime, "%Y%m%d%H"))) 
        elif granularity == 'day':   
         markertime = linetime[0:-4] 
         markertime_epoch = int(time.mktime(time.strptime(markertime, "%Y%m%d"))) 
        elif granularity == 'all':   
         markertime = totime 
         markertime_epoch = int(time.mktime(time.strptime(totime, "%Y%m%d%H%M"))) 
        client = lineparts[linetime_index-1].split(':')
        clientip = client[0]
        timings = lineparts[timings_index].split('/')
        tq = int(timings[0])
        tr = int(timings[3])
        tt = int(timings[4])
        ttr = int(tt) - int(tr)
        status = int(lineparts[status_index])
        size = int(lineparts[size_index])
        restcall = []
        if len(lineparts) == base_index:
         restcall = lineparts[base_index-1]
        elif len(lineparts) == base_index+2:
         verb = lineparts[base_index-1][1:]
         restcall = lineparts[base_index].split('?')
        elif len(lineparts) == base_index+3:
         verb = lineparts[base_index][1:]
         restcall = lineparts[base_index+1].split('?')
        elif len(lineparts) == base_index+4:
         verb = lineparts[base_index+1][1:]
         restcall = lineparts[base_index+2].split('?')
        url = restcall[0].split('/')
        if len(restcall) > 1:
         params = restcall[1]
        if len(url) == 2: # database level call
         if url[1].startswith('dashboard.'):
          database = 'dashboard-client'
         else:
          database = url[1]
         endpoint = 'none'
        elif len(url) == 3: 
         if url[1].startswith('dashboard.'):
          database = 'dashboard-client'
         else:
          database = url[1]
         if len(url[2]) == 0: 
          endpoint = 'none'
         elif url[2].startswith('_'):
          endpoint = url[2]
         else:
          endpoint = 'document-level' 
        elif len(url) > 3:
         if url[1].startswith('dashboard.'):
          database = 'dashboard-client'
         else:
          database = url[1]
         if url[2].startswith('_design') and len(url)>4:
          endpoint = url[2]+url[4]
         elif url[2].startswith('_'):
          endpoint = url[2]
         else:
          endpoint = 'document-level' 
        if (int(linetime) >= int(fromtime)) and (int(linetime) < int(totime)):
          if not exclude_entry(database,verb,endpoint,exclusions) and not exclude_client(clientip,exclusions):
            thislist.append([clusterurl,loghost,database,linetime,markertime,markertime_epoch,verb,tq,tr,tt,ttr,status,size,endpoint])
        return linetime 
     except Exception as e:
        return 0 
    else:
       return 0 

def find_dbstats(logfile,fromtime,totime,granularity,exclusions,loghost,cluster_url):
   linetime_format,linetime_index,linetime_start,linetime_end,\
    timings_index,status_index,size_index,base_index = process_collectconfig('/opt/cloudant-specialapi/perfagent_collect.conf')
   linedbstatlist=[]
   if os.path.isfile(logfile):
     lf = None
     if logfile[-3:] == '.gz':
      lf = gzip.open(logfile,'r')
     elif logfile[-3:] == '.bz2':
      lf = bz2.open(logfile,'r')
     else:
      lf = open(logfile,'r')
     line = lf.readline()
     linecount = 1
     pticker=0
     startlinefound = False
     endlinefound = False
     while ((line != '') and not endlinefound):
      linetime = process_dbstatline(line,fromtime,totime,linedbstatlist,granularity,exclusions,loghost,cluster_url,\
        linetime_format,linetime_index,linetime_start,linetime_end,timings_index,status_index,size_index,base_index)
      if not startlinefound:
       if int(linetime) >= int(fromtime):
        startlinefound = True
        logging.warn('{cloudant performance agent} Start of time boundary detected <' + str(fromtime) + '> at line <'+str(linecount)+'>')
      if int(linetime) >= int(totime):
        endlinefound = True
        logging.warn('{cloudant performance agent} End of time boundary detected <' + str(totime) + '> at line <'+str(linecount)+'>')
      line = lf.readline()
      linecount = linecount+1
     if not startlinefound:
      print('{cloudant performance agent} No lines found for selected collection period starting <' + str(fromtime) + '>')
      logging.warn('{cloudant performance agent} No lines found for selected collection period starting <' + str(fromtime) + '>')
     lf.close()
   return pd.DataFrame(linedbstatlist,columns=['cluster','loghost','database','ltime','mtime', 'mtime_epoch','verb','tq','tr','tt','ttr','status','size','endpoint'])

def get_groups(stats,groupcriteria):
    try:
      methods =  stats.groupby(groupcriteria,as_index=False)
      st2_dbstats = stats[(stats['status']>=200) & (stats['status']<300)]
      st3_dbstats = stats[(stats['status']>=300) & (stats['status']<400)]
      st4_dbstats = stats[(stats['status']>=400) & (stats['status']<500)]
      st5_dbstats = stats[(stats['status']>=500) & (stats['status']<600)]
      st2_methods =  st2_dbstats.groupby(groupcriteria,as_index=False)
      st3_methods =  st3_dbstats.groupby(groupcriteria,as_index=False)
      st4_methods =  st4_dbstats.groupby(groupcriteria,as_index=False)
      st5_methods =  st5_dbstats.groupby(groupcriteria,as_index=False)
      tq = (methods['tq'].agg({'tqmin':np.min,'tqmax':np.max,'tqavg':np.mean,'tqsum':np.sum,'tqcount':np.size})).round(1)
      tr = (methods['tr'].agg({'trmin':np.min,'trmax':np.max,'travg':np.mean,'trsum':np.sum,'trcount':np.size})).round(1)
      tt = (methods['tt'].agg({'ttmin':np.min,'ttmax':np.max,'ttavg':np.mean,'ttsum':np.sum,'ttcount':np.size})).round(1)
      ttr = (methods['ttr'].agg({'ttrmin':np.min,'ttrmax':np.max,'ttravg':np.mean,'ttrsum':np.sum,'ttrcount':np.size})).round(1)
      st2 = (st2_methods['status'].agg({'st2min':np.min,'st2max':np.max,'st2avg':np.mean,'st2sum':np.sum,'st2count':np.size})).round(1)
      st3 = (st3_methods['status'].agg({'st3min':np.min,'st3max':np.max,'st3avg':np.mean,'st3sum':np.sum,'st3count':np.size})).round(1)
      st4 = (st4_methods['status'].agg({'st4min':np.min,'st4max':np.max,'st4avg':np.mean,'st4sum':np.sum,'st4count':np.size})).round(1)
      st5 = (st5_methods['status'].agg({'st5min':np.min,'st5max':np.max,'st5avg':np.mean,'st5sum':np.sum,'st5count':np.size})).round(1)
      sz = (methods['size'].agg({'szmin':np.min,'szmax':np.max,'szavg':np.mean,'szsum':np.sum,'szcount':np.size})).round(1)
      op1 = pd.merge(tq,tr,on=groupcriteria)
      op2 = pd.merge(op1,tt,on=groupcriteria)
      op3 = pd.merge(op2,ttr,on=groupcriteria)
      op4 = pd.merge(op3,sz,on=groupcriteria)
      op5 = pd.merge(op4,st2,on=groupcriteria,how='outer').fillna(0)
      op6 = pd.merge(op5,st3,on=groupcriteria,how='outer').fillna(0)
      op7 = pd.merge(op6,st4,on=groupcriteria,how='outer').fillna(0)
      op8 = pd.merge(op7,st5,on=groupcriteria,how='outer').fillna(0)
      op8[['st2count','st3count','st4count','st5count']] = op8[['st2count','st3count','st4count','st5count']].astype(int)
      op8['stfailpct'] = op8.apply(lambda row: 100*(row['st3count']+row['st4count']+row['st5count']) /(row['st2count']+row['st3count']+row['st4count']+row['st5count']), axis=1)
      return op8
    except Exception as e:
      print e
      return None

def read_exclusions(efile):
   exclusions = []
   if os.path.isfile(efile):
    ef = open(efile,'r')
    lines = ef.readlines()
    for l in lines:
     try:
      thisExclusion = eval(l)
      exclusions.append(dict(thisExclusion))
     except:
      pass
    ef.close()
   return exclusions

def read_thresholds(tfile):
   thresholds = []
   if os.path.isfile(tfile):
    tf = open(tfile,'r')
    lines = tf.readlines()
    for l in lines:
     try:
      thisThreshold = eval(l)
      thresholds.append(dict(thisThreshold))
     except:
      pass
    tf.close()
   return thresholds

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


def match_resourcekey(database,verb,endpoint,thresholds):
    match = False
    metric_conditions = []
    index = 0
    while index < len(thresholds):
      if test_field(thresholds,index,'database',database):
       if test_field(thresholds,index,'verb',verb):
        if test_field(thresholds,index,'endpoint',endpoint): 
          match = True
          metric_conditions.append([thresholds[index]['metric'],thresholds[index]['operator'],thresholds[index]['limit'],\
           thresholds[index]['qualifier'],thresholds[index]['qoperator'],thresholds[index]['qlimit']])
      index = index + 1
    return match,metric_conditions

def test_condition(operator,limit,value):
    if operator == '<':
     if value < limit:
      return True 
    elif operator == '<=':
     if value <= limit:
      return True
    elif operator == '>=':
     if value >= limit:
      return True
    elif operator == '>':
     if value > limit:
      return True
    elif operator == '==':
     if value == limit:
      return True
    elif operator == '!=':
     if value != limit:
      return True
    else:
     return False

 
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

def get_resource_key(row,scope):
    key = ''
    if scope == 'endpoint':
     key = 'Database='+getattr(row,'database')+',Verb='+getattr(row,'verb')+',Endpoint='+getattr(row,'endpoint')
    elif scope == 'verb':
     key = 'Database='+getattr(row,'database')+',Verb='+getattr(row,'verb')
    elif scope == 'database':
     key = 'Database='+getattr(row,'database')
    elif scope == 'all':
     key = 'Cluster=All'
    return key

       
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
      columns=['mtime','mtime_epoch','tqmin','tqavg','tqmax','tqcount','tqsum','trmin','travg','trmax','trcount','trsum',\
               'ttmin','ttavg','ttmax','ttcount','ttsum','ttrmin','ttravg','ttrmax','ttrcount','ttrsum',\
               'szmin','szavg','szmax','szcount','szsum','st2count','st3count','st4count','st5count','stfailpct'] 
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
