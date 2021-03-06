import json
import datetime
import sys
import os
import base64
import logging
import api_utils
import time
import requests
from perfagent_menu import *

def process_timeperiod(fromtime):
    if fromtime is None:
      ftime = datetime.datetime.now().strftime("%Y%m%d%H%M")
    else:
      ftime = re.sub('[\/_\:-]','',fromtime)
    return ftime

def log_entry(location,filename,istring):
      if os.path.exists(location):
        lf = open(location+'/'+filename,'a')
        lf.write(str(istring)+'\n')
        lf.flush()
        lf.close()

def execute_hostdata_collect(sess,clusterurl,fromtime,resultid,results_location):
 try:
    mtime = fromtime
    mtime_epoch = int(time.mktime(time.strptime(mtime, "%Y%m%d%H%M")))
    start_epoch = int(mtime_epoch - 59)
    smooshfile = 'smooshstats_'+str(fromtime)+'_'+str(resultid)+'.csv'
    smooshcolumns = 'index,cluster,host,channel,mtime,mtime_epoch,active,waiting,starting'
    log_entry(results_location,smooshfile,smooshcolumns)
    ioqfile = 'ioqtypestats_'+str(fromtime)+'_'+str(resultid)+'.csv'
    ioqcolumns = 'index,cluster,host,ioqtype,mtime,mtime_epoch,requests'
    log_entry(results_location,ioqfile,ioqcolumns)
    hostfile = 'hoststats_'+str(fromtime)+'_'+str(resultid)+'.csv'
    hostcolumns = 'index,cluster,host,mtime,mtime_epoch,doc_writes,doc_inserts,ioql_max,ioql_med,ioql_pctl_90,ioql_pctl_99,ioql_pctl_999'
    log_entry(results_location,hostfile,hostcolumns)

    skey= str(start_epoch)+'000'
    ekey = str(mtime_epoch)+'000'
    smoosh_response = api_utils.get_with_retries(sess,clusterurl+'/metrics/_design/system_view/_view/system?startkey=["uptime",'+\
                        skey+']&endkey=["uptime",'+ekey+']&include_docs=true',2,None)
    if smoosh_response is not None:
      smooshdata = smoosh_response.json()
      cindex = 0
      if 'rows' in smooshdata:
       for hostdata in smooshdata['rows']:
        if 'doc' in hostdata:
         if 'smoosh' in hostdata['doc']:
           channels = hostdata['doc']['smoosh']['channels']
           for channel in channels:
               channelstring = str(cindex)+','+str(clusterurl)+','+str(hostdata['value']['host'])+','+str(channel)+','+\
                str(mtime)+','+str(mtime_epoch)+','+\
                str(channels[channel]['active'])+','+str(channels[channel]['waiting'])+','+str(channels[channel]['starting'])
               log_entry(results_location,smooshfile,channelstring) 
               cindex = cindex+1
    ioq_response = api_utils.get_with_retries(sess,clusterurl+'/metrics/_design/stats_view/_view/stats?startkey=["ioq_requests",'+\
                        skey+']&endkey=["ioq_requests",'+ekey+']',2,None)
    if ioq_response is not None:
      ioqdata = ioq_response.json()
      qindex = 0
      if 'rows' in ioqdata:
       for ioqtype in ioqdata['rows']:
        ioqstring = str(qindex)+','+str(clusterurl)+','+str(ioqtype['value']['host'])+','+str(ioqtype['value']['id'])+','+\
         str(mtime)+','+str(mtime_epoch)+','+\
         str(ioqtype['value']['value'])
        log_entry(results_location,ioqfile,ioqstring) 
        qindex=qindex+1
    hoststat = []
    docrw_response = api_utils.get_with_retries(sess,clusterurl+'/metrics/_design/stats_view/_view/stats?startkey=["document_rdwr",'+\
                        skey+']&endkey=["document_rdwr",'+ekey+']',2,None)
    if docrw_response is not None:
      docrwdata = docrw_response.json()
      if 'rows' in docrwdata:
       for doctype in docrwdata['rows']:
          if not any(d.get('host', None) == doctype['value']['host'] for d in hoststat):
           hoststat.append({'host':doctype['value']['host']})
       for x in range(0,len(hoststat)):
         for doctype in docrwdata['rows']:
           if hoststat[x]['host'] == doctype['value']['host']:
             if doctype['value']['id'] == 'document_writes':
               hoststat[x]['writes'] = doctype['value']['value']  
             elif doctype['value']['id'] == 'document_inserts':
               hoststat[x]['inserts'] = doctype['value']['value']  
    ioql_response = api_utils.get_with_retries(sess,clusterurl+'/metrics/_design/stats_view/_view/stats?startkey=["ioq_latency",'+\
                        skey+']&endkey=["ioq_latency",'+ekey+']',2,None)
    if ioql_response is not None:
      ioqldata = ioql_response.json()
      if 'rows' in ioqldata:
       for doctype in ioqldata['rows']:
          if not any(d.get('host', None) == doctype['value']['host'] for d in hoststat):
           hoststat.append({'host':doctype['value']['host']})
       for x in range(0,len(hoststat)):
         for doctype in ioqldata['rows']:
           if hoststat[x]['host'] == doctype['value']['host']:
             if doctype['value']['id'] == 'max':
               hoststat[x]['ioql_max'] = doctype['value']['value']  
             elif doctype['value']['id'] == 'median':
               hoststat[x]['ioql_med'] = doctype['value']['value']  
             elif doctype['value']['id'] == 90:
               hoststat[x]['ioql_pctl_90'] = doctype['value']['value']  
             elif doctype['value']['id'] == 99:
               hoststat[x]['ioql_pctl_99'] = doctype['value']['value']  
             elif doctype['value']['id'] == 999:
               hoststat[x]['ioql_pctl_999'] = doctype['value']['value']  
    for x in range(0,len(hoststat)):
      hoststring = str(x)+','+str(clusterurl)+','+str(hoststat[x]['host'])+','+\
      str(mtime)+','+str(mtime_epoch)+','+\
      str(hoststat[x]['writes'])+','+str(hoststat[x]['inserts'])+','+\
      str(hoststat[x]['ioql_max'])+','+str(hoststat[x]['ioql_med'])+','+\
      str(hoststat[x]['ioql_pctl_90'])+','+str(hoststat[x]['ioql_pctl_99'])+','+ str(hoststat[x]['ioql_pctl_99'])
      log_entry(results_location,hostfile,hoststring) 
    return True
 except Exception as e:
  logging.warn('{Cloudant hostdata (from metricsdb) agent collector} Error : '+str(e))
  return False
 
defaults_file = "/opt/cloudant-performancecollector/resources/collect/configuration/perfagent.conf"
logfilename = '/var/log/cloudant_hostdata_collector.log'
logging.basicConfig(filename = logfilename, level=logging.WARN,
                    format='%(asctime)s[%(funcName)-5s] (%(processName)-10s) %(message)s',
                    )

try:    
  requests.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
  requests.urllib3.disable_warnings(requests.packages.urllib3.exceptions.SubjectAltNameWarning)
except:
  try:
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.SubjectAltNameWarning)
  except:
    logging.warn("{Cloudant hostdata (from metricsdb) performance worker} Unable to disable urllib3 warnings")
    pass


if __name__ == '__main__':
 try:

    opts, args = options()
    valid_selection = False

    default_connectioninfo, default_certificate_verification,default_requests_ca_bundle,default_inputlogfile,default_thresholdsfile,\
     default_eventsexclusionsfile,default_statsexclusionsfile,default_scope,default_granularity,\
     default_performercount, default_resultslocation, default_outputformat = process_defaults_config(defaults_file)

    if not opts.resultslocation:
       opts.resultslocation = default_resultslocation

    if default_certificate_verification == 'True':
       opts.certverif = True
       if os.path.exists(default_requests_ca_bundle):
          os.environ['REQUESTS_CA_BUNDLE'] = default_requests_ca_bundle
       else:
          print("REQUESTS_CA_BUNDLE file ["+str(default_requests_ca_bundle)+"] does not exist - all sessions will fail")
          logging.warn("REQUESTS_CA_BUNDLE file ["+str(default_requests_ca_bundle)+"] does not exist - all sessions will fail")
    else:
       opts.certverif = False

    if not opts.connectioninfo:
       opts.connectioninfo = default_connectioninfo

    s_url,s_credentials,s_username,s_password,p_url = process_connection_info(opts.connectioninfo)

    if s_url is None or s_credentials is None or s_username is None or s_password is None:
          print("perfagent: Cannot process connection info [" + str(opts.connectioninfo) + "]")
          logging.warn("{Cloudant hostdata (from metricsdb) performance worker} Cannot process connection info [" + str(opts.connectioninfo) + "]")
          sys.exit(1)
    else:
      logging.warn("{Cloudant hostdata (from metricsdb) performance worker} Startup") 
      sess,sresp,scookie = api_utils.create_cluster_session(s_url,s_username, s_password,p_url,opts.certverif)
      if sess == None:
        logging.warn("Cloudant hostdata (from metricsdb) performance worker} Cluster Access Error : Session Rejected")
      elif sresp is None:
        logging.warn("Cloudant hostdata (from metricsdb) performance worker} Cluster Access Error : Session No response")
      elif sresp.status_code > 250:
        logging.warn("Cloudant hostdata (from metricsdb) performance worker} Cluster Access Error : Session Error ["+str(sresp.status_code)+"]")
      else:
              opts.fromtime = process_timeperiod(opts.fromtime)
              resultid = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
              response = execute_hostdata_collect(sess,s_url,opts.fromtime,resultid,opts.resultslocation)
              if response: 
                    logging.warn('{Cloudant hostdata (from metricsdb) performance worker} Processing Completed Successfully for Entry ['+resultid+']') 
              else:
                logging.warn('{Cloudant hostdata (from metricsdb) performance worker} Processing Failed for Entry ['+resultid+']') 
      api_utils.close_cluster_session(sess,s_url)
 except Exception as e:
  logging.warn("cloudant hostdata (from metricsdb) performance worker : Unexpected Shutdown : Reason ["+str(e)+"]")
