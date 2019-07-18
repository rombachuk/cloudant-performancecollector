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
      docs['tqdoc'] = {"cluster": lineparts[rindex], "loghost": lineparts[rindex+1], "database": lineparts[rindex+2], "verb": lineparts[rindex+3], "timestamp":lineparts[tindex],
      "min":lineparts[tqindex],"avg":lineparts[tqindex+1],"max":lineparts[tqindex+2],"count":lineparts[tqindex+3],"sum":lineparts[tqindex+4]}
      docs['trdoc'] = {"cluster": lineparts[rindex], "loghost": lineparts[rindex+1], "database": lineparts[rindex+2], "verb": lineparts[rindex+3], "timestamp":lineparts[tindex],
                        "min":lineparts[trindex],"avg":lineparts[trindex+1],"max":lineparts[trindex+2],"count":lineparts[trindex+3],"sum":lineparts[trindex+4]}
     return docs 
    except Exception as e:
     logging.warn("{proxydata elasticsearch exporter} Request Processing Unexpected  Error : "+str(e))

def export_line_docs(es,linedocs,scope):
    try:
     if scope == 'verb':
      tqres=es.index(index='proxy_verb',doc_type='tq',id=linedocs['id']+'0',body=linedocs['tqdoc'])
      trres=es.index(index='proxy_verb',doc_type='tq',id=linedocs['id']+'1',body=linedocs['trdoc'])
      print(str(tqres))
      print(str(trres))
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
