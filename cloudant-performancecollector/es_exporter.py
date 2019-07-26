import time
import datetime
import string
import logging
import os
import re
import base64
import subprocess 
import requests
from optparse import OptionParser
from proxydata_esexport import execute_exportproxy
from clientdata_esexport import execute_exportclient
from hostdata_esexport import execute_exporthost
from volumedata_esexport import execute_exportvolume
from bodydata_esexport import execute_exportbody

def process_config_file(cfile):
    resultslocation = '/opt/cloudant-performancecollector/results'
    if cfile and os.path.isfile(cfile):
      cf = open(cfile,'r')
      cflines = cf.readlines()
      for cfline in cflines:
          cflineparts = cfline.split()
          if len(cflineparts) == 2 and cflineparts[0] == 'resultslocation':
             resultslocation = cflineparts[1]
    return resultslocation

def process_connection_file(cfile):
    url = 'http://elastichost:9200'
    ssl = 'disabled'
    certficate = '/opt/cloudant-performancecollector/resources/export/elasticsearch/configuration/certificates/ca.pem'
    username = 'user'
    password = 'pass'
    if cfile and os.path.isfile(cfile):
      cf = open(cfile,'r')
      cflines = cf.readlines()
      for cfline in cflines:
          cflineparts = cfline.split()
          if len(cflineparts) == 2 and cflineparts[0] == 'url':
             url = cflineparts[1]
          if len(cflineparts) == 2 and cflineparts[0] == 'ssl':
             ssl = cflineparts[1]
          elif len(cflineparts) == 2 and cflineparts[0] == 'certificate':
             certificate = cflineparts[1]
          elif len(cflineparts) == 2 and cflineparts[0] == 'credentials':
             source_credentials = cflineparts[1]
             src_credparts = str(base64.urlsafe_b64decode(source_credentials)).split(':')
             if len(src_credparts) == 2:
                username = src_credparts[0]
                password = src_credparts[1].strip()
          else:
             pass
      cf.close()
    return url,ssl,certificate,username,password  

def options():
    parser = OptionParser()
    parser.add_option("-d",
                      "--data")
    parser.add_option("-f",
                      "--fromtime",
                      help="start time in time range format granularity day YYYYMMDDHHMM eg 201711301100 [default none]")
    parser.add_option("-g",
                      "--granularity")
    parser.add_option("-s",
                      "--scope")
    parser.add_option("-t",
                      "--totime",
                      help="start time in time range format granularity day YYYYMMDDHHMM eg 201711301100 [default none]")
    opts, args = parser.parse_args()
    return opts, args


def process_fromperiod(fromtime):
    if fromtime is None:
      ftime = datetime.datetime.now().strftime("%Y%m%d%H%M")
    else: 
      ftime = re.sub('[\/_\:-]','',fromtime) 
    return ftime

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
    logging.warn("{perfagent esexporter} Unable to disable urllib3 warnings")
    pass

conf_file = "/opt/cloudant-performancecollector/resources/export/elasticsearch/configuration/perfagent_es.conf"
connection_file = "/opt/cloudant-performancecollector/resources/export/elasticsearch/configuration/perfagent_es_connection.info"
logfilename = "/var/log/cloudant_data_esexporter.log"

logging.basicConfig(filename = logfilename, level=logging.WARN,
                    format='%(asctime)s[%(funcName)-5s] (%(processName)-10s) %(message)s',
                    )

if __name__ == "__main__":
    opts, args = options()
    valid_selection = False
    
    results_location = process_config_file(conf_file)
    es_url,es_ssl,es_cert,es_username,es_password = process_connection_file(connection_file)
    
    if es_url is None or es_username is None or es_password is None: 
          print("perfagent_es_exporter: Cannot process connection info [" + str(connection_file) + "]")
          sys.exit(1)
    
    if es_ssl == 'enabled' and os.path.exists(es_cert):
          os.environ['REQUESTS_CA_BUNDLE'] = es_cert 
    else:
          print("REQUESTS_CA_BUNDLE file ["+str(es_cert)+"] does not exist - all sessions will fail")
          logging.warn("REQUESTS_CA_BUNDLE file ["+str(es_cert)+"] does not exist - all sessions will fail")

    if opts.data == 'proxy' or opts.data == 'client'  or opts.data == 'body'  or opts.data == 'host' or opts.data == 'volume':
       valid_data = True
    else:
       valid_data = False

    if not opts.scope or opts.scope == 'endpoint'  or opts.scope == 'verb' or opts.scope == 'body':
       if not opts.scope:
         opts.scope = 'verb'
       valid_scope = True
    else:
       valid_granularity = False

    if not opts.granularity or opts.granularity == 'minute'  or  opts.granularity == 'hour'  or opts.granularity == 'day' or opts.granularity == 'second':
       if not opts.granularity:
         opts.granularity = 'minute'
       valid_granularity = True
    else:
       valid_granularity = False
 
    if opts.data == 'volume':
       opts.fromtime = process_fromperiod(opts.fromtime) 
       if len(opts.fromtime) == 12:
        execute_exportvolume(es_url,es_username,es_password,es_ssl,es_cert,\
               opts.fromtime,results_location)
        valid_selection = True
    
    if opts.data == 'host':
       opts.fromtime = process_fromperiod(opts.fromtime) 
       if len(opts.fromtime) == 12:
        execute_exporthost(es_url,es_username,es_password,es_ssl,es_cert,\
               opts.fromtime,results_location)
        valid_selection = True
    
    if opts.data == 'client' and valid_scope and valid_granularity: 
       opts.fromtime,opts.totime = process_timeperiod(opts.fromtime,opts.totime) 
       if len(opts.fromtime) == 12 and len(opts.totime) == 12:
        execute_exportclient(es_url,es_username,es_password,es_ssl,es_cert,\
               opts.fromtime,opts.totime,opts.granularity,opts.scope,results_location)
        valid_selection = True
    
    if opts.data == 'proxy' and valid_scope and valid_granularity: 
       opts.fromtime,opts.totime = process_timeperiod(opts.fromtime,opts.totime) 
       if len(opts.fromtime) == 12 and len(opts.totime) == 12:
        execute_exportproxy(es_url,es_username,es_password,es_ssl,es_cert,\
               opts.fromtime,opts.totime,opts.granularity,opts.scope,results_location)
        valid_selection = True
    
    if opts.data == 'body' and valid_scope and valid_granularity: 
       opts.fromtime,opts.totime = process_timeperiod(opts.fromtime,opts.totime) 
       if len(opts.fromtime) == 12 and len(opts.totime) == 12:
        execute_exportbody(es_url,es_username,es_password,es_ssl,es_cert,\
               opts.fromtime,opts.totime,opts.granularity,opts.scope,results_location)
        valid_selection = True
    
    if not valid_selection:
       print "perfagent_es_exporter: Command not recognised"
