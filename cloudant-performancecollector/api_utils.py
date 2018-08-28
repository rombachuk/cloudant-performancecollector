from flask import request
import json
import time
import datetime
import requests
import logging
import string
import urllib
import sys
import base64
import os
import shutil
from pwd import getpwuid
from grp import getgrgid
import re

def is_int(s):
    try:
        int(s)
        return True
    except TypeError,ValueError:
        return False

def check_ownership(filename,owner,group):
    try:
        thisowner = getpwuid(os.stat(filename).st_uid).pw_name
        thisgroup = getgrgid(os.stat(filename).st_gid).gr_name
        if thisowner == owner and thisgroup == group:
          return True
        else:
          return False
    except:
        return False

def get_with_retries(c_session, uri, max_attempts, specialheaders):
    get_response = None
    attempts = 0
    retry = True
    while retry and attempts < max_attempts:
      if specialheaders is None:
       get_response = c_session.get(uri,verify=False)
      else:
       get_response = c_session.get(uri,headers=specialheaders,verify=False)
      if get_response is not None:
       if get_response.status_code == 400:
         attempts = attempts + 1
       else:
         retry = False
    if attempts >= max_attempts:
     logging.warn("{persistent 400} content=["+str(get_response.content)+"]")
    return get_response
         
def get_doc_rev(c_session,url,id):
    get_url = url + '/' + id
    get_response = get_with_retries(c_session,get_url,10,None)
    if get_response is None:
       logging.warn("Get Document Revision Session get error: No response")
    elif get_response.status_code == 404:
       pass
    elif get_response.status_code > 250:
       data = get_response.json()
       if data['reason'] != 'deleted':
          logging.warn("Get Document Revision Session get error: " + str(get_response.status_code))
       return ""
    else:
       data = get_response.json()
       if data == None:
        return ""
       elif not '_rev' in data:
        return "" 
       elif len(data['_rev']) > 0:
        return data['_rev'] 
       else:
        return ""

def get_ddoc(filename):
    ddoc = None
    full_file = '/opt/cloudant-specialapi/'+filename
    if os.path.exists(full_file):
      f = open(full_file,'r')
      ddoc =  f.read()
      f.close()
    return ddoc

def get_template(filename):
    doc = None
    if os.path.exists(filename):
      f = open(filename,'r')
      doc =  f.read()
      f.close()
    return doc

def set_index_db(c_session,url,db,indexdoc):
      db_url = url+'/'+db + '/_index'
      json_doc = json.loads(indexdoc)
      thisrev = get_doc_rev(c_session,url+'/'+db,'_index')
      if len(thisrev) == 0:
        doc_response = c_session.post(db_url,data=json.dumps(json_doc),headers={'content-type':'application/json'})
      if doc_response is None:
        logging.warn("Set Index DB Session put error: No response")
        return False
      if doc_response.status_code > 250:
        logging.warn("Set Index DB Session put error: " + str(doc_response.status_code))
        return False
      else:
        data = doc_response.json()
        if 'error' in data:
           logging.warn("Set Index DB Session put error: " + str(data))
           return False
        else:
          return True

def set_permissions_db(c_session,url,db,securitydoc):
    try:
      db_url = url+'/'+db + '/_security'
      json_doc = json.loads(securitydoc)
      thisrev = get_doc_rev(c_session,url+'/'+db,'_security')
      if thisrev is not None:
       if len(thisrev) > 0:
        json_doc['_rev'] = thisrev 
      doc_response = c_session.put(db_url,data=json.dumps(json_doc),headers={'content-type':'application/json'})
      if doc_response is None:
        logging.warn("Set Permissions DB Session put error: No response")
        return False
      if doc_response.status_code > 250:
        logging.warn("Set Permissions DB Session put error: " + str(doc_response.status_code))
        return False
      else:
        data = doc_response.json()
        if 'error' in data:
           logging.warn("Set Permissions DB Session put error: " + str(data))
           return False
        else:
          return True
    except Exception as e:
     logging.warn("Set Permissions DB Exception: " + str(e))
    return False

def get_permissions_db(c_session,url,db):
    db_url = url + '/' + db + '/_security'
    get_response = get_with_retries(c_session,db_url,10,None)
    if get_response is None:
       logging.warn("Get Permissions DB Session get error: No response")
       return None
    elif get_response.status_code == 404:
       logging.warn("Get Permissions DB Session get error: Not found")
       return None
    elif get_response.status_code > 250:
       logging.warn("Check Permissions DB Session get error: " + str(get_response.status_code))
       return None
    else:
       return get_response.json()

def adminparty_db(c_session,url,db): 
       name_entries = 0
       role_entries = 0
       data = get_permissions_db(c_session,url,db)
       if data != None:
        if 'members' in data:
         if 'names' in data['members']:
           name_entries = len(data['members']['names']) 
         if 'roles' in data['members']:
           role_entries = len(data['members']['roles'])
        if name_entries == 0 and role_entries == 0:
         logging.warn("{cbcon security} World-open permissions found for  ["+db+"] on cluster ["+url+"]")
         return True
        else:
         return False
       else:
        logging.warn("{cbcon security} World-open permissions found for  ["+db+"] on cluster ["+url+"]")
        return True 

def enforce_permissions_db(c_session,url,db,template):
         logging.warn("{cbcon health} Enforcing permissions for db ["+db+"] on cluster ["+url+"] using template ["+template+"]")
         template_doc = get_template(template)
         set_result = set_permissions_db(c_session,url,db,template_doc)
         return set_result

def exists_db(c_session,url,db):
    db_url = url + '/' + db
    get_response = get_with_retries(c_session,db_url,10,None)
    if get_response is None:
       logging.warn("Check Exists DB Session get error: No response")
    elif get_response.status_code == 404:
       data = get_response.json()
       if 'error' in data:
	if data['error'] == 'not_found':
           return False
    elif get_response.status_code > 250:
       logging.warn("Check Exists DB Session get error: " + str(get_response.status_code))
       return True
    else:
       return True 

def close_cluster_session(c_session,url):
    try:  
          delresponse = None
          delresponse = c_session.delete(url+'/_session')
          return delresponse
    except requests.exceptions.ConnectionError,e:
          return delresponse

def create_cluster_session(url,username,password,proxyurl,certverif):
    try:
          this_session = None
          this_session_response = None
          this_session_cookie = None
          login_data = {'name':username,'password':password}
          headers = {'Accept':'application/json','Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
          this_session = requests.session()
          if proxyurl is not None:
            proxies = {'http':proxyurl}
            if certverif == True:
              this_session_response = this_session.post(url + '/_session',data=login_data,headers=headers,proxies=proxies,verify=True)
            else:
              this_session_response = this_session.post(url + '/_session',data=login_data,headers=headers,proxies=proxies,verify=False)
          else:  
            if certverif == True:     
              this_session_response = this_session.post(url + '/_session',data=login_data,headers=headers,verify=True)
            else:
              this_session_response = this_session.post(url + '/_session',data=login_data,headers=headers,verify=False)
          if 'Set-Cookie' in this_session_response.headers:
            this_session_cookie = this_session_response.headers['Set-Cookie']
          return this_session, this_session_response,this_session_cookie
    except requests.exceptions.ConnectionError,e:
          return this_session, this_session_response,this_session_cookie

def process_config(cfile):
    clusterurl = ''
    admincredentials = ''
    migrateapi_status = 'disabled'
    managedbapi_status = 'disabled'
    perfagentapi_status = 'disabled'
    if cfile and os.path.isfile(cfile):
      cf = open(cfile,'r')
      cflines = cf.readlines()
      for cfline in cflines:
          cflineparts = cfline.split()
          if len(cflineparts) == 2 and cflineparts[0] == 'clusterurl': 
            clusterurl = cflineparts[1]
          elif len(cflineparts) == 2 and cflineparts[0] == 'admincredentials': 
            admincredentials = cflineparts[1]
          elif len(cflineparts) == 2 and cflineparts[0] == 'migrateapi_status': 
            migrateapi_status = cflineparts[1]
          elif len(cflineparts) == 2 and cflineparts[0] == 'managedbapi_status': 
            managedbapi_status = cflineparts[1]
          elif len(cflineparts) == 2 and cflineparts[0] == 'perfagentapi_status': 
            perfagentapi_status = cflineparts[1]
          else:
            pass
      cf.close()
    return clusterurl,admincredentials,migrateapi_status,managedbapi_status,perfagentapi_status

def create_db(c_session,url,db,adminuser):
   if not exists_db(c_session,url,db):
    url_enc = url + '/' + db
    dbcreate_response = c_session.put(url_enc,
        headers={'content-type': 'application/json'})
    if dbcreate_response is None:
        print("Error creating db [" + db +"] : No response from cluster")
        logging.warn("Error creating db [" + db +"] : No response from cluster")
        return False
    elif dbcreate_response.status_code > 250:
        print("Error creating db [" + db +"] : " + str(dbcreate_response.status_code))
        logging.warn("Error creating db [" + db + "] : " + str(dbcreate_response.status_code))
        return False
    else:
        securitydoc = '{"admins":{"names":["'+adminuser+'"],"roles":[]},"members":{"names":["'+adminuser+'"],"roles":[]}}' 
        set_permissions_db(c_session,url,db,securitydoc)
        statusindex = '{"index":{"fields":["qtime","status","db","ddid"]},"type":"json"}'
        set_index_db(c_session,url,db,statusindex)
        return True
   else:
    return True

def create_adminsession(url,username, password):
    proxyurl = None
    certverif = False
    adminsession,adminsession_response,adminsession_cookie =  create_cluster_session(url,username,password,proxyurl,certverif)
    if adminsession is None:
     error_response = {'error': 'API Access Error'}
     error_code = 400
    elif adminsession_response is None:
     error_response = {'error': 'API Access Error'}
     error_code = 400
    elif adminsession_response.status_code > 250:
     error_response = {'error': 'API Access Session Error ('+str(adminsession_response.status_code)+')'}
     error_code = adminsession_response.status_code
    else:
     error_response = None
     error_code = 200
    return adminsession,error_response,error_code

def find_requestuser(request):
 try:
  auth = request.authorization
  if auth:
   return auth.username
  else:
   cookieauth = request.cookies.get("AuthSession")
   if cookieauth is not None:
    cookieauthparts = str(base64.urlsafe_b64decode(str(cookieauth))).split(':')
    if len(cookieauthparts) > 1:
     return cookieauthparts[0]
  return None
 except Exception as e:
  return None
