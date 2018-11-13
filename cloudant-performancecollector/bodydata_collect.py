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
import api_utils

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

def process_body_dbstatline(thisline,fromtime,totime,thislist,granularity,exclusions,loghost,clusterurl,\
        linetime_format,linetime_index,linetime_start,linetime_end, timings_index,status_index,size_index,base_index): 
    database='unknown'
    verb='unknown'
    endpoint='unknown'
    clientip='unknown'
    params='-'
    selector='-'
    body='-'
    thislineparts = []
    http = False
    if 'HTTP/1' in thisline:
     http = True
     thislineparts = thisline.split()
     i = 0
     basefound = False
     while i < len(thislineparts) and not basefound:
      if 'HTTP/1' in thislineparts[i]:
       basefound = True
      else:
       i=i+1
     lineparts = thislineparts[:(i+1)]
     if 'HTTP/1' in thislineparts[len(thislineparts)-1]:
       selector = '-'
     else:
       selector = thislineparts[len(thislineparts)-1]
    else: 
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
        base_offset = len(lineparts) - base_index
        if not http:
         verb = lineparts[len(lineparts)-2][1:]
         restcall = lineparts[len(lineparts)-1].split('?')
        else:
         verb = lineparts[base_index+base_offset-3][1:]
         restcall = lineparts[base_index+base_offset-2].split('?')
        url = restcall[0].split('/')
        if len(restcall) > 1:
         params = restcall[1]
        if len(url) > 1:
          database = str(url[1])
        if len(url) == 2 and database == '_session' and verb == 'POST':
          endpoint = 'logon'
        if len(url) == 2 and database == '_session' and verb == 'DELETE':
          endpoint = 'logoff'
        if len(url) == 2 and database != '_session':
          endpoint = 'dbinfo'
        if len(url) > 2:
          es = str(url[2]);
          for i in range(3,len(url)):
           es = es + '/' + str(url[i])
          endpoint = es
        if len(url) == 3 and not str(url[2]).startswith('_'):
          endpoint = 'singledocument'
        elif len(url) == 4 and str(url[2]).startswith('_local'):
          endpoint = 'replicationdocument'
        elif database == 'metrics_app' and 'statistics' in endpoint:
          endpoint = 'metricsdashboard'
        elif '"<BADREQ>"' in thisline:
          database = 'BADREQUEST'
          verb = 'BADREQUEST'
          endpoint = 'BADREQUEST'
        if verb == "POST" and "queries" in selector and '"include_docs":true' in selector and "startkey" in selector :
          body = "startkey_includetrue"
        elif verb == "POST" and "queries" in selector and '"include_docs":false' in selector and "startkey" in selector :
          body = "startkey_includefalse"
        elif verb == "POST" and "queries" in selector and '"include_docs":true' in selector and "keys" in selector :
          body = "keys_includetrue"
        elif verb == "POST" and "queries" in selector and '"include_docs":false' in selector and "keys" in selector :
          body = "keys_includefalse"
        elif verb == "POST" and "queries" in selector and '"include_docs":true' in selector and not "keys" in selector and not "startkey" in selector and "key" in selector:
          body = "singlekey_includetrue"
        elif verb == "POST" and "queries" in selector and '"include_docs":false' in selector and not "keys" in selector and not "startkey" in selector and "key" in selector:
          body = "singlekey_includefalse"
        if (int(linetime) >= int(fromtime)) and (int(linetime) < int(totime)):
          if not exclude_entry(database,verb,endpoint,exclusions) and not exclude_client(clientip,exclusions):
            thislist.append([clusterurl,loghost,clientip,linetime,markertime,markertime_epoch,database,verb,endpoint,body,tq,tr,tt,ttr,status,size])
        return linetime 
     except Exception as e:
        return 0 
    else:
       return 0 

def find_body_dbstats(logfile,fromtime,totime,granularity,exclusions,loghost,cluster_url):
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
      linetime = process_body_dbstatline(line,fromtime,totime,linedbstatlist,granularity,exclusions,loghost,cluster_url,\
        linetime_format,linetime_index,linetime_start,linetime_end,timings_index,status_index,size_index,base_index)
      if not startlinefound:
       if int(linetime) >= int(fromtime):
        startlinefound = True
        logging.warn('{cloudant body data collector} Start of time boundary detected <' + str(fromtime) + '> at line <'+str(linecount)+'>')
      if int(linetime) >= int(totime):
        endlinefound = True
        logging.warn('{cloudant body data collector} End of time boundary detected <' + str(totime) + '> at line <'+str(linecount)+'>')
      line = lf.readline()
      linecount = linecount+1
     if not startlinefound:
      print('{cloudant body data collector} No lines found for selected collection period starting <' + str(fromtime) + '>')
      logging.warn('{cloudant body data collector} No lines found for selected collection period starting <' + str(fromtime) + '>')
     lf.close()
   return pd.DataFrame(linedbstatlist,columns=['cluster','loghost','client','ltime','mtime', 'mtime_epoch','database','verb','endpoint','body','tq','tr','tt','ttr','status','size'])

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

 

def get_resource_key(row,scope):
    key = ''
    if scope == 'endpoint':
     key = 'Client='+getattr(row,'client')+',Verb='+getattr(row,'verb')+',Endpoint='+getattr(row,'endpoint')
    elif scope == 'verb':
     key = 'Client='+getattr(row,'client')+',Verb='+getattr(row,'verb')
    elif scope == 'database':
     key = 'Client='+getattr(row,'client')
    elif scope == 'all':
     key = 'Client=All'
    return key

       

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
      basestats = find_body_dbstats(inputlogfile,fromtime,totime,granularity,read_exclusions(statsexclusionsfile),loghost,cluster_url)
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


def process_timeperiod(fromtime,totime):
    if totime is None or totime == 'now':
      ttime = datetime.datetime.now().strftime("%Y%m%d%H%M")
    else: 
      ttime = re.sub('[\/_\:-]','',totime) 
    if fromtime is None:
      ftime = (datetime.datetime.now() - datetime.timedelta(hours=2)).strftime("%Y%m%d%H%M")
    else: 
      ftime = re.sub('[\/_\:-]','',fromtime) 
    return ftime,ttime 
    

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
    elif opts.granularity == 'minute'  or  opts.granularity == 'hour'  or opts.granularity == 'day' or opts.granularity == 'all':
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
