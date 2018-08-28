import time
import datetime
import string
import logging
import os
import re
import subprocess 
import requests
from perfagent_menu import *
from perfagent_collect import *
import api_utils

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
    logging.warn("{cloudant performance agent} Unable to disable urllib3 warnings")
    pass

defaults_file = "/opt/cloudant-specialapi/perfagent.conf"
logfilename = "/var/log/cloudant_perfagent.log"

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
       opts.statsexclusionsfile = default_statsexclusionsfile

    if not opts.scope:
       opts.scope = default_scope
       valid_scope = True
    elif opts.scope == 'document'  or  opts.scope == 'endpoint'  or opts.scope == 'verb' or opts.scope == 'database' or opts.scope == 'all':
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
          print("perfagent: Cannot process connection info [" + str(opts.connectioninfo) + "]")
          sys.exit(1)
         
    if opts.scope and valid_granularity:
          opts.fromtime,opts.totime = process_timeperiod(opts.fromtime,opts.totime) 
          if len(opts.fromtime) == 12 and len(opts.totime) == 12:
              resultsid = datetime.datetime.now().strftime("%Y%m%d%H%M%f")
              execute_collect(opts.scope,s_url,s_credentials,s_username,s_password,p_url,opts.certverif,\
               opts.inputlogfile,opts.thresholdsfile,opts.eventsexclusionsfile,opts.statsexclusionsfile,\
               opts.fromtime,opts.totime,opts.granularity,opts.performercount,opts.resultslocation,resultsid,opts.outputformat,opts.logfilehost,s_url)
              valid_selection = True
    
    if not valid_selection:
       print "perfagent: Command not recognised"
