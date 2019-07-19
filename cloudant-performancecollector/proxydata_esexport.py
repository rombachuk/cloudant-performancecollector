import base64
import bz2
import gzip
import logging
import datetime
import time
import subprocess
import select
import re
import os
import json
from es_utils import es_connect


def find_line_indexes(scope):
     if scope == "endpoint":
      idindex = 0
      rindex = 1
      tindex = 7
      tqindex = 8 
      tcindex = 13
      trindex = 18
      ttindex = 23
      ttrindex = 28
      szindex = 33
      feindex = 38
      beindex = 43
      stcountindex = 48
     elif scope == "verb":
      idindex = 0
      rindex = 1
      tindex = 6
      tqindex = 7 
      tcindex = 12
      trindex = 17
      ttindex = 22
      ttrindex = 27
      szindex = 32
      feindex = 37
      beindex = 42
      stcountindex = 47
     return idindex,rindex,tindex,tqindex,tcindex,trindex,ttindex,ttrindex,szindex,feindex,beindex,stcountindex

def get_line_docs(lineparts,scope):
    try:
     docs = {}
     idindex,rindex,tindex,tqindex,tcindex,trindex,ttindex,ttrindex,szindex,feindex,beindex,stcountindex = find_line_indexes(scope)
     if scope == 'verb':
      docs['id'] = str(lineparts[tindex])+str(lineparts[idindex])
      docs['tqdoc'] = {"metric": "tq", "cluster": lineparts[rindex], "loghost": lineparts[rindex+1], "database": lineparts[rindex+2], "verb": lineparts[rindex+3], "timestamp":lineparts[tindex],
      "min":lineparts[tqindex],"avg":lineparts[tqindex+1],"max":lineparts[tqindex+2],"count":lineparts[tqindex+3],"sum":lineparts[tqindex+4]}
      docs['tcdoc'] = {"metric": "tc","cluster": lineparts[rindex], "loghost": lineparts[rindex+1], "database": lineparts[rindex+2], "verb": lineparts[rindex+3], "timestamp":lineparts[tindex],
                        "min":lineparts[tcindex],"avg":lineparts[tcindex+1],"max":lineparts[tcindex+2],"count":lineparts[tcindex+3],"sum":lineparts[tcindex+4]}
      docs['trdoc'] = {"metric": "tr","cluster": lineparts[rindex], "loghost": lineparts[rindex+1], "database": lineparts[rindex+2], "verb": lineparts[rindex+3], "timestamp":lineparts[tindex],
                        "min":lineparts[trindex],"avg":lineparts[trindex+1],"max":lineparts[trindex+2],"count":lineparts[trindex+3],"sum":lineparts[trindex+4]}
      docs['ttdoc'] = {"metric": "tt","cluster": lineparts[rindex], "loghost": lineparts[rindex+1], "database": lineparts[rindex+2], "verb": lineparts[rindex+3], "timestamp":lineparts[tindex],
                        "min":lineparts[ttindex],"avg":lineparts[ttindex+1],"max":lineparts[ttindex+2],"count":lineparts[ttindex+3],"sum":lineparts[ttindex+4]}
      docs['ttrdoc'] = {"metric": "ttr","cluster": lineparts[rindex], "loghost": lineparts[rindex+1], "database": lineparts[rindex+2], "verb": lineparts[rindex+3], "timestamp":lineparts[tindex],
                        "min":lineparts[ttrindex],"avg":lineparts[ttrindex+1],"max":lineparts[ttrindex+2],"count":lineparts[ttrindex+3],"sum":lineparts[ttrindex+4]}
      docs['szdoc'] = {"metric": "sz","cluster": lineparts[rindex], "loghost": lineparts[rindex+1], "database": lineparts[rindex+2], "verb": lineparts[rindex+3], "timestamp":lineparts[tindex],
                        "min":lineparts[szindex],"avg":lineparts[szindex+1],"max":lineparts[szindex+2],"count":lineparts[szindex+3],"sum":lineparts[szindex+4]}
      docs['fedoc'] = {"metric": "fe","cluster": lineparts[rindex], "loghost": lineparts[rindex+1], "database": lineparts[rindex+2], "verb": lineparts[rindex+3], "timestamp":lineparts[tindex],
                        "min":lineparts[feindex],"avg":lineparts[feindex+1],"max":lineparts[feindex+2],"count":lineparts[feindex+3],"sum":lineparts[feindex+4]}
      docs['bedoc'] = {"metric": "be","cluster": lineparts[rindex], "loghost": lineparts[rindex+1], "database": lineparts[rindex+2], "verb": lineparts[rindex+3], "timestamp":lineparts[tindex],
                        "min":lineparts[beindex],"avg":lineparts[beindex+1],"max":lineparts[beindex+2],"count":lineparts[beindex+3],"sum":lineparts[beindex+4]}
      docs['stdoc'] = {"metric": "st","cluster": lineparts[rindex], "loghost": lineparts[rindex+1], "database": lineparts[rindex+2], "verb": lineparts[rindex+3], "timestamp":lineparts[tindex],
                        "count_status_200":lineparts[stcountindex],"count_status_300":lineparts[stcountindex+1],"count_status_400":lineparts[stcountindex+2],"count_status_500":lineparts[stcountindex+3],"pct_fail_status":lineparts[stcountindex+4]}
     return docs 
    except Exception as e:
     logging.warn("{proxydata elasticsearch exporter} Request Processing Unexpected  Error : "+str(e))

def export_line_docs(es,linedocs,scope):
    try:
     if scope == 'verb':
      tqres=es.index(index='proxy_verb',doc_type="_doc",id=linedocs['id']+'0',body=linedocs['tqdoc'])
      tcres=es.index(index='proxy_verb',doc_type="_doc",id=linedocs['id']+'1',body=linedocs['tcdoc'])
      trres=es.index(index='proxy_verb',doc_type="_doc",id=linedocs['id']+'2',body=linedocs['trdoc'])
      ttres=es.index(index='proxy_verb',doc_type="_doc",id=linedocs['id']+'3',body=linedocs['ttdoc'])
      ttrres=es.index(index='proxy_verb',doc_type="_doc",id=linedocs['id']+'4',body=linedocs['ttrdoc'])
      szres=es.index(index='proxy_verb',doc_type="_doc",id=linedocs['id']+'5',body=linedocs['szdoc'])
      feres=es.index(index='proxy_verb',doc_type="_doc",id=linedocs['id']+'6',body=linedocs['fedoc'])
      beres=es.index(index='proxy_verb',doc_type="_doc",id=linedocs['id']+'7',body=linedocs['bedoc'])
      stres=es.index(index='proxy_verb',doc_type="_doc",id=linedocs['id']+'8',body=linedocs['stdoc'])
      return True 
    except Exception as e:
     logging.warn("{proxydata elasticsearch exporter} Request Processing Unexpected  Error : "+str(e))
     return False

def execute_exportproxy(url,username,password,ssl,cert,fromtime,totime,granularity,scope,resultslocation):
   try: 
      if os.path.exists(resultslocation):
       filestart = "stats_"+str(scope)+"_by_"+str(granularity)+"_"+str(fromtime)+"_to_"+str(totime)
       for filename in os.listdir(resultslocation):
        if filename.startswith(filestart):
           logging.warn("{proxydata elasticsearch exporter} exporting from file ["+str(filename)+"]") 
           es = es_connect(url,username,password,ssl,cert)                     
           ef = open(resultslocation+'/'+filename,'r')
           eflines = ef.readlines()
           lines_success = 0
           lines_fail = 0
           for efline in eflines:
            if not 'mtime' in efline:
              eflineparts = efline.split(',') 
              linedocs = get_line_docs(eflineparts,scope)
              result = export_line_docs(es,linedocs,scope)
              if result:
               lines_success = lines_success + 1
              else:
               lines_fail = lines_fail + 1 
           print("success=["+str(lines_success)+"] fail=["+str(lines_fail)+"]")
           return True
      else:
       logging.warn("{proxydata elasticsearch exporter} resultslocation ["+str(resultslocation)+"] not found*")
       return False 
   except Exception as e:
      filestart = "stats_"+str(scope)+"_by_"+str(granularity)+"_"+str(fromtime)+"_"+str(totime)
      logging.warn("{proxydata elasticsearch exporter} Request Processing Unexpected  Error : "+str(e))
      logging.warn("{proxydata elasticsearch exporter} exporting from file ["+str(filestart)+"*]")
      return False 
