from flask import request, Response
import json
import datetime
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

class Opts:
    pass

def process_attribute(opts,params,fulloption,shortoption):
    if params.get(fulloption,type=str):
     setattr(opts,fulloption,params.get(fulloption,type=str))
    elif params.get(shortoption,type=str):
     setattr(opts,fulloption,params.get(shortoption,type=str))

def process_requestparams(params):
    opts = Opts() 
    process_attribute(opts,params,'eventsexclusionsfile','E') 
    process_attribute(opts,params,'fromtime','f') 
    process_attribute(opts,params,'granularity','g') 
    process_attribute(opts,params,'logfilehost','H') 
    process_attribute(opts,params,'inputlogfile','L') 
    process_attribute(opts,params,'outputformat','O') 
    process_attribute(opts,params,'performercount','p') 
    process_attribute(opts,params,'resultslocation','R') 
    process_attribute(opts,params,'scope','s') 
    process_attribute(opts,params,'statsexclusionfile','S') 
    process_attribute(opts,params,'totime','t') 
    process_attribute(opts,params,'thresholdsfile','T') 
    process_attribute(opts,params,'connectioninfo','x') 
    return opts

def process_opts(params):
    opts = process_requestparams(params)
    valid_scope = False
    valid_granularity = False
    valid_timeboundary = False
    defaults_file = "/opt/cloudant-specialapi/perfagent.conf"
    default_connectioninfo, default_certificate_verification,default_requests_ca_bundle,default_inputlogfile,default_thresholdsfile,\
    default_eventsexclusionsfile,default_statsexclusionsfile,default_scope,default_granularity,\
    default_performercount, default_resultslocation,default_outputformat = process_defaults_config(defaults_file)
    if default_certificate_verification == 'True':
       opts.certverif = True
       if os.path.exists(default_requests_ca_bundle):
         os.environ['REQUESTS_CA_BUNDLE'] = default_requests_ca_bundle
       else:
         logging.warn("REQUESTS_CA_BUNDLE file ["+str(default_requests_ca_bundle)+"] does not exist - all sessions will fail")
    else:
       opts.certverif = False

    if not hasattr(opts,'inputlogfile'):
       opts.inputlogfile = default_inputlogfile

    if not hasattr(opts,'thresholdsfile'):
       opts.thresholdsfile = default_thresholdsfile

    if not hasattr(opts,'eventsexclusionsfile'):
       opts.eventsexclusionsfile = default_eventsexclusionsfile

    if not hasattr(opts,'statsexclusionsfile'):
       opts.statsexclusionsfile = default_statsexclusionsfile

    if not hasattr(opts,'scope'):
       opts.scope = default_scope
       valid_scope = True
    elif opts.scope == 'document'  or  opts.scope == 'endpoint'  or opts.scope == 'verb' or opts.scope == 'database' or opts.scope == 'all':
       valid_scope = True
    else:
       valid_scope = False

    if not hasattr(opts,'granularity'):
       opts.granularity = default_granularity
       valid_granularity = True
    elif opts.granularity == 'minute'  or  opts.granularity == 'hour'  or opts.granularity == 'day' or opts.granularity == 'all':
       valid_granularity = True
    else:
       valid_granularity = False

    if not hasattr(opts,'outputformat'):
       opts.outputformat = default_outputformat
    elif not (opts.outputformat == 'csv'  or  opts.outputformat == 'json'):
       opts.outputformat = default_outputformat

    if not hasattr(opts,'performercount'):
       opts.performercount = default_performercount

    if not hasattr(opts,'resultslocation'):
       opts.resultslocation = default_resultslocation

    if not hasattr(opts,'logfilehost'):
       opts.logfilehost = ''

    if not hasattr(opts,'connectioninfo'):
       opts.connectioninfo = default_connectioninfo

    if hasattr(opts,'scope') and valid_granularity:
          if not hasattr(opts,'fromtime'):
            opts.fromtime = None
          if not hasattr(opts,'totime'):
            opts.totime = None
          opts.fromtime,opts.totime = process_timeperiod(opts.fromtime,opts.totime)
          if len(opts.fromtime) == 12 and len(opts.totime) == 12:
            valid_timeboundary = True
    return opts,valid_scope,valid_granularity,valid_timeboundary

def process_post(request,sess):
    try:
     opts,scope_ok,gran_ok,times_ok = process_opts(request.args)
     requestuser = api_utils.find_requestuser(request)
     if requestuser is None:
      requestuser = 'unknown'
     if scope_ok and gran_ok and times_ok:
      now = datetime.datetime.now()
      qtime = now.strftime("%Y%m%d%H%M%S%f")
      submitted = now.strftime("%Y-%m-%d %H:%M:%S.%f")
      id = qtime
      jsonopts = opts.__dict__
      qdoc = {"opts":opts.__dict__,"qtime":qtime,"requester":requestuser,"submitted":submitted,"status":"submitted"}
      put_response = sess.put(request.url_root+'apiperfagentqueue/'+id,data=json.dumps(qdoc),headers={'content-type':'application/json'})
      if put_response is None:
       return {'error': 'API Access Error'},400
      elif put_response.status_code == 404:
       return {'error': 'API Access Error - DB not found'},404
      elif put_response.status_code > 250:
       return {'error': 'API Access Session Error ('+str(put_response.status_code)+')'},put_response.status_code
      else:
       data = put_response.json()
       datastring = json.dumps(data)
       return datastring,None
    except Exception as e:
      return {'error': 'API Processing Error'+str(e)},500

def process_get(request,sess,docid):
     get_response = api_utils.get_with_retries(sess,request.url_root+'apiperfagentqueue/'+docid,5, None)
     if get_response is None:
      return {'error': 'API Access Error'},400
     elif get_response.status_code == 404:
      return {'error': 'API Access Error - Performance Agent Request Document not found'},404
     elif get_response.status_code > 250:
      return {'error': 'API Access Session Error ('+str(get_response.status_code)+')'},get_response.status_code
     else:
      data = get_response.json()
      datastring = json.dumps(data)
      return datastring,None 

