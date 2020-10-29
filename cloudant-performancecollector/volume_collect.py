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

def execute_volumedata_collect(sess,clusterurl,fromtime,resultid,results_location):
 try:
  mtime = fromtime 
  mtime_epoch = int(time.mktime(time.strptime(mtime, "%Y%m%d%H%M")))
  start_epoch = int(mtime_epoch - 59)
  dbfile = 'dbvolumestats_'+str(fromtime)+'_'+str(resultid)+'.csv'
  dbcolumns = 'index,cluster,database,mtime,mtime_epoch,doc_count,del_doc_count,disk_size,data_size,shard_count'
  log_entry(results_location,dbfile,dbcolumns)
  viewfile = 'viewvolumestats_'+str(fromtime)+'_'+str(resultid)+'.csv'
  viewcolumns = 'index,cluster,database,viewdoc,view,signature,mtime,mtime_epoch,disk_size,data_size,active_size,updates_pending_total,updates_pending_minimum,updates_pending_preferred,shard_count'
  log_entry(results_location,viewfile,viewcolumns)
  alldbs_response = api_utils.get_with_retries(sess,clusterurl+'/_all_dbs',2,None)
  if alldbs_response is None:
    logging.warn('cloudant volume collector:  all dbs list: collection failed')
    return None
  else:
    data = alldbs_response.json()
    if '_replicator' not in data:
        logging.warn('cloudant volume collector:  all dbs list: collection failed')
        return None
    logging.warn('cloudant volume collector:  all dbs list [{}]: collection success'.format(str(len(data))))
    index = 0
    for db in data:
      db=db.replace('/','%2F')
      db_response = api_utils.get_with_retries(sess,clusterurl+'/'+str(db),2,None)
      shards_response = api_utils.get_with_retries(sess,clusterurl+'/'+str(db)+'/_shards',2,None)
       
      if db_response is not None:
        dbdata = db_response.json()
        if 'doc_count' not in dbdata:
           logging.warn('cloudant volume collector:  db [{}] : Error : collection failed'.format(db))
        else:
            logging.warn('cloudant volume collector:  db [{}] : collection success'.format(db))
            shardcount = 0
            if shards_response is not None:
                shardsdata = shards_response.json()
                if 'shards' in shardsdata:
                    shardcount = len(shardsdata['shards'])
            dbstring = str(index)+','+str(clusterurl)+','+str(db)+','+str(mtime)+','+str(mtime_epoch)+','+str(dbdata['doc_count'])+','+\
            str(dbdata['doc_del_count'])+','+str(dbdata['disk_size'])+','+str(dbdata['data_size'])+','+str(shardcount)
            log_entry(results_location,dbfile,dbstring)
      index = index+1
    vindex = 0
    for db in data:
      db=db.replace('/','%2F')
      dbviews_response = api_utils.get_with_retries(sess,clusterurl+'/'+str(db)+'/_all_docs?start_key="_design"&end_key="_design0"',2,None)
      shards_response = api_utils.get_with_retries(sess,clusterurl+'/'+str(db)+'/_shards',2,None)
      if dbviews_response is not None:
       shardcount = 0
       if shards_response is not None:
         shardsdata = shards_response.json()
         if 'shards' in shardsdata:
           shardcount = len(shardsdata['shards'])
       dbviewsdata = dbviews_response.json()
       if 'rows' in dbviewsdata:
         for view in dbviewsdata['rows']:
           view_response = api_utils.get_with_retries(sess,clusterurl+'/'+str(db)+'/'+str(view['id'])+'/_info',2,None)
           if view_response is not None:
              viewdata = view_response.json()
              if 'view_index' in viewdata:
               logging.warn('cloudant volume collector:  db [{}] view [{}]: collection success'.format(db,str(view['id'])))
               viewindex = viewdata['view_index']
               viewstring = str(vindex)+','+str(clusterurl)+','+str(db)+','+str(view['id'])+','+str(viewdata['name'])+','+str(viewindex['signature'])+','+\
               str(mtime)+','+str(mtime_epoch)+','+\
               str(viewindex['disk_size'])+','+str(viewindex['data_size'])+','+str(viewindex['sizes']['active'])+','+\
               str(viewindex['updates_pending']['total'])+','+str(viewindex['updates_pending']['minimum'])+','+str(viewindex['updates_pending']['preferred'])+','+str(shardcount)
               log_entry(results_location,viewfile,viewstring) 
           vindex = vindex +1

    return True
 except Exception as e:
  logging.warn('cloudant volume collector:  Error : '+str(e))
  return False
 
defaults_file = "/opt/cloudant-performancecollector/resources/collect/configuration/perfagent.conf"
logfilename = '/var/log/cloudant_volumedata_collector.log'
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
    logging.warn("cloudant volume collector: Error: Unable to disable urllib3 warnings")
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
          print("Cloudant volume performancecollector: Cannot process connection info [" + str(opts.connectioninfo) + "]")
          logging.warn("{Cloudant volume performancecollector worker} Cannot process connection info [" + str(opts.connectioninfo) + "]")
          sys.exit(1)
    else:
      logging.warn("{Cloudant volume collector worker} Startup") 
      sess,sresp,scookie = api_utils.create_cluster_session(s_url,s_username, s_password,p_url,opts.certverif)
      if sess == None:
        logging.warn("Cloudant volume performancecollector worker} Cluster Access Error : Session Rejected")
      elif sresp is None:
        logging.warn("Cloudant volume performancecollector worker} Cluster Access Error : Session No response")
      elif sresp.status_code > 250:
        logging.warn("Cloudant volume performancecollector worker} Cluster Access Error : Session Error ["+str(sresp.status_code)+"]")
      else:
              opts.fromtime = process_timeperiod(opts.fromtime)
              resultid = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
              response = execute_volumedata_collect(sess,s_url,opts.fromtime,resultid,opts.resultslocation)
              if response: 
                    logging.warn('{Cloudant volume performancecollector worker} Volume Processing Completed Successfully for Entry ['+resultid+']') 
              else:
                logging.warn('{Cloudant volume performancecollector worker} Volume Data Collection Processing Failed for Entry ['+resultid+']') 
      api_utils.close_cluster_session(sess,s_url)
 except Exception as e:
  logging.warn("cloudant volume performancecollector worker : Unexpected Shutdown : Reason ["+str(e)+"]")
