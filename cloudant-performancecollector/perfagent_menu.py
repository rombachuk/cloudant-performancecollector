import datetime
import string
import sys
import base64
import os
import re
from optparse import OptionParser

def process_defaults_config(cfile):
    default_connectioninfo = '/opt/cloudant-specialapi/perfagent_connection.info'
    default_certificate_verification = False
    default_requests_ca_bundle = '/opt/cloudant-specialapi/ca.pem'
    default_inputlogfile = '/var/log/haproxy.log'
    default_thresholdsfile = '/opt/cloudant-specialapi/perfagent_thresholds.info'
    default_eventsexclusionsfile = '/opt/cloudant-specialapi/perfagent_eventsexclusions.info'
    default_statsexclusionsfile = '/opt/cloudant-specialapi/perfagent_statsexclusions.info'
    default_scope = 'endpoint'
    default_granularity = 'hour'
    default_performercount = 10
    default_resultslocation = '/opt/cloudant-specialapi/perfagent_results'
    default_outputformat = 'csv'
    if cfile and os.path.isfile(cfile):
      cf = open(cfile,'r')
      cflines = cf.readlines()
      for cfline in cflines:
          cflineparts = cfline.split()
          if len(cflineparts) == 2 and cflineparts[0] == 'default_connectioninfo':
             default_connectioninfo = cflineparts[1] 
          elif len(cflineparts) == 2 and cflineparts[0] == 'default_certificate_verification':
             default_certificate_verification = cflineparts[1] 
          elif len(cflineparts) == 2 and cflineparts[0] == 'default_requests_ca_bundle':
             default_requests_ca_bundle = cflineparts[1] 
          elif len(cflineparts) == 2 and cflineparts[0] == 'default_inputlogfile':
             default_inputlogfile = cflineparts[1] 
          elif len(cflineparts) == 2 and cflineparts[0] == 'default_thresholdsfile':
             default_thresholdsfile = cflineparts[1] 
          elif len(cflineparts) == 2 and cflineparts[0] == 'default_eventsexclusionsfile':
             default_eventsexclusionsfile = cflineparts[1] 
          elif len(cflineparts) == 2 and cflineparts[0] == 'default_statsexclusionsfile':
             default_statsexclusionsfile = cflineparts[1] 
          elif len(cflineparts) == 2 and cflineparts[0] == 'default_scope':
             default_scope = cflineparts[1] 
          elif len(cflineparts) == 2 and cflineparts[0] == 'default_granularity':
             default_granularity = cflineparts[1] 
          elif len(cflineparts) == 2 and cflineparts[0] == 'default_performercount':
             default_performercount = cflineparts[1] 
          elif len(cflineparts) == 2 and cflineparts[0] == 'default_resultslocation':
             default_resultslocation = cflineparts[1] 
          elif len(cflineparts) == 2 and cflineparts[0] == 'default_outputformat':
             default_outputformat = cflineparts[1] 
          else:
 	     pass
      cf.close()
    return default_connectioninfo, default_certificate_verification,default_requests_ca_bundle,default_inputlogfile,\
           default_thresholdsfile, default_eventsexclusionsfile,default_statsexclusionsfile,default_scope,default_granularity,\
           default_performercount, default_resultslocation, default_outputformat


def process_connection_info(cinfo):
    source_url = None
    source_credentials = None
    source_username = None
    source_password = None
    proxy_url = None
    if cinfo and os.path.isfile(cinfo):
      cf = open(cinfo,'r')
      cflines = cf.readlines()
      for cfline in cflines:
          cflineparts = cfline.split()
          if len(cflineparts) == 2 and cflineparts[0] == 'sourceurl':
             source_url = cflineparts[1] 
          if len(cflineparts) == 2 and cflineparts[0] == 'sourceBase64':
             source_credentials = cflineparts[1] 
             src_credparts = str(base64.urlsafe_b64decode(source_credentials)).split(':')
             if len(src_credparts) == 2:
                source_username = src_credparts[0]
                source_password = src_credparts[1]
          elif len(cflineparts) == 2 and cflineparts[0] == 'proxyurl':
             proxy_url = cflineparts[1] 
          else:
 	     pass
      cf.close()
    return source_url,source_credentials,source_username,source_password,proxy_url


def options():
    parser = OptionParser()
    parser.add_option("-E",
                      "--eventsexclusionsfile",
                      help="file containing the exclusions to be applied for threshold checking")
    parser.add_option("-f",
                      "--fromtime",
                      help="start time in time range format granularity day YYYYMMDDHHMM eg 201711301100 [default none]")
    parser.add_option("-g",
                      "--granularity",
                      help="granularity of aggregated measurements in units of minutes")
    parser.add_option("-H",
                      "--logfilehost",
                      help="host providing logfile")
    parser.add_option("-L",
                      "--inputlogfile",
                      help="log file in haproxy.log type to process")
    parser.add_option("-O",
                      "--outputformat",
                      help="json or csv, default is csv")
    parser.add_option("-p",
                      "--performercount",
                      help="number of high or worst performers to detect")
    parser.add_option("-R",
                      "--resultslocation",
                      help="directory where results files are to be placed")
    parser.add_option("-s",
                      "--scope",
                      help="command to perform [default none]")
    parser.add_option("-S",
                      "--statsexclusionsfile",
                      help="file containing the exclusions to be applied for stats calculations")
    parser.add_option("-t",
                      "--totime",
                      help="end time in time range format granularity day YYYYMMDDHHMM eg 201711301200 [default none]")
    parser.add_option("-T",
                      "--thresholdsfile",
                      help="file containing the thresholds to be applied and used to generate events")
    parser.add_option("-x",
                      "--connectioninfo",
                      help="file containing source and destination info [default none]")
    opts, args = parser.parse_args()
    return opts, args


