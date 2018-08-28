import json
import datetime
import sys
import os
import base64
import logging
import api_utils
import migrateapi
import time

def process_queue(sess,clusterurl,db):
    try:
     query = { "selector": { "status": { "$eq": "submitted" } },"sort":[{"qtime":"asc"}] }
     query_response = sess.post(clusterurl+'/'+db+'/_find',data=json.dumps(query),headers={'content-type':'application/json'})
     if query_response is None:
      return {'error': 'Queue Access Error'},400
     elif query_response.status_code == 404:
      return {'error': 'Queue Access Error - DB not found'},404
     elif query_response.status_code > 250:
      return {'error': 'Queue Access Session Error ('+str(put_response.status_code)+')'},put_response.status_code
     else:
      data = query_response.json()
      if 'docs' not in data:
       return {'error': 'Queue Error - Empty'},404
      elif len(data['docs']) == 0:
       return {'error': 'Queue Error = Empty'},404
      else:
        qdata = data['docs'] 
        return qdata,None 
    except Exception as e:
      return {'error': 'Queue Processing Error'+str(e)},500 

def update_queue_entry(sess,clusterurl,qitem,db,status,info,response):
 try:
  thisrev = api_utils.get_doc_rev(sess,clusterurl+'/'+db,qitem['_id'])
  thisdoc = qitem
  if len(thisrev) > 0:
   thisdoc['_rev'] = thisrev
  thisdoc['status'] = status
  if info is not None:
   thisdoc['info'] = info
  if response is not None:
   thisdoc['response'] = response
  now = datetime.datetime.now()
  thisdoc['updated'] = now.strftime("%Y-%m-%d %H:%M:%S.%f")
  if status == 'success' or status == 'failed':
   thisdoc['completed'] = now.strftime("%Y-%m-%d %H:%M:%S.%f")
  doc_response = sess.put(clusterurl+'/'+db+'/'+qitem['_id'],data=json.dumps(thisdoc),headers={'content-type':'application/json'}) 
  if doc_response is None:
        logging.warn("{worker queue update} Update Status Error: No response")
        return False
  elif doc_response.status_code > 250:
        logging.warn("{worker queue update} Update Status Error : " + str(doc_response.status_code))
        return False
  else:
        return True 
 except Exception as e:
  logging.warn("{worker queue update} Update Status Error : " + str(e))
  return False

