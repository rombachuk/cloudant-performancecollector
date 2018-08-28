import json
import datetime
import sys
import os
import base64
import logging
import api_utils
from perfagent_collect import execute_collect 
from perfagent_menu import process_connection_info
from worker_utils import process_queue,update_queue_entry
import time
import requests

adminuser = ''
adminpwd = ''

logfilename = '/var/log/perfagentworker.log'
logging.basicConfig(filename = logfilename, level=logging.WARN,
                    format='%(asctime)s[%(funcName)-5s] (%(processName)-10s) %(message)s',
                    )

try:    
  requests.urllib3.disable_warnings()
except:
  try:
    requests.packages.urllib3.disable_warnings()
  except:
    logging.warn("{perfagent worker} Unable to disable urllib3 warnings")
    pass


if __name__ == '__main__':
 try:
   logging.warn("{perfagent worker} Startup") 
   clusterurl,creds,migrateapi_status,managedbapi_status,perfagentapi_status = api_utils.process_config('/opt/cloudant-specialapi/csapi.conf')
   credparts = str(base64.urlsafe_b64decode(str(creds))).split(':')
   if len(credparts) == 2:
    adminuser = credparts[0]
    adminpwd = credparts[1]
    while True:
     sess,serr,scode = api_utils.create_adminsession(clusterurl,adminuser, adminpwd)
     if serr != None:
      logging.warn(str(serr)+'/'+str(scode))
     else:
      qdata,qcode = process_queue(sess,clusterurl,'apiperfagentqueue') 
      if qdata is not None:
       if not 'error' in qdata: 
        for qitem in qdata:
         logging.warn('{perfagent worker} Executing Performance Agent Processing for Entry ['+qitem['_id']+']') 
	 update_queue_entry(sess,clusterurl,qitem,'apiperfagentqueue',"processing",None,None)
         if 'opts' in qitem:
          opts = qitem['opts']
          s_url,s_credentials,s_username,s_password,p_url = process_connection_info(opts['connectioninfo'])
          if s_url is not None and s_credentials is not None and s_username is not None and s_password is not None:
              response = execute_collect(opts['scope'],s_url,s_credentials,s_username,s_password,p_url,opts['certverif'],\
               opts['inputlogfile'],opts['thresholdsfile'],opts['eventsexclusionsfile'],opts['statsexclusionsfile'],\
               opts['fromtime'],opts['totime'],opts['granularity'],opts['performercount'],opts['resultslocation'],\
               qitem['_id'],opts['outputformat'],opts['logfilehost'],clusterurl)
              if response is not None:
                if 'stats' in response:
                  if response['stats'] == []:
                    update_queue_entry(sess,clusterurl,qitem,'apiperfagentqueue',"failed","No statistics found for requested options and exclusions",response)
                    logging.warn('{perfagent worker} Performance Agent Processing Failed for Entry ['+qitem['_id']+']') 
                  else:
                    update_queue_entry(sess,clusterurl,qitem,'apiperfagentqueue',"success",None,response)
                    logging.warn('{perfagent worker} Performance Agent Processing Completed Successfully for Entry ['+qitem['_id']+']') 
                elif 'statsfile' in response:
                  if response['statsfile'] == '':
                    update_queue_entry(sess,clusterurl,qitem,'apiperfagentqueue',"failed","No statistics found for requested options and exclusions",response)
                    logging.warn('{perfagent worker} Performance Agent Processing Failed for Entry ['+qitem['_id']+']') 
                  else:
                    update_queue_entry(sess,clusterurl,qitem,'apiperfagentqueue',"success",None,response)
                    logging.warn('{perfagent worker} Performance Agent Processing Completed Successfully for Entry ['+qitem['_id']+']') 
                else:
                  update_queue_entry(sess,clusterurl,qitem,'apiperfagentqueue',"failed","No statistics found for requested options and exclusions",response)
                  logging.warn('{perfagent worker} Performance Agent Processing Failed for Entry ['+qitem['_id']+']') 
              else:
                update_queue_entry(sess,clusterurl,qitem,'apiperfagentqueue',"failed","Processing Error : No response",None)
                logging.warn('{perfagent worker} Performance Agent Processing Failed for Entry ['+qitem['_id']+']') 
          else:
            update_queue_entry(sess,clusterurl,qitem,'apiperfagentqueue',"failed","Invalid Options",None)
            logging.warn('{perfagent worker} Performance Agent Processing Failed for Entry ['+qitem['_id']+']') 
         else:
           update_queue_entry(sess,clusterurl,qitem,'apiperfagentqueue',"failed","Invalid Options",None)
           logging.warn('{perfagent worker} Performance Agent Processing Failed for Entry ['+qitem['_id']+']') 
       elif 'error' in qdata and qdata['error'] != "Queue Error = Empty": 
        logging.warn("{perfagent worker} Error in processing queue ["+str(qdata)+"] Code ["+str(qcode)+"]")
     api_utils.close_cluster_session(sess,clusterurl)
     time.sleep(10)
 except Exception as e:
  logging.warn("Cloudant perfagent worker : Unexpected Shutdown : Reason ["+str(e)+"]")
