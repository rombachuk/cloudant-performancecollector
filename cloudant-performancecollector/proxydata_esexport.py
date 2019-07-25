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
from es_utils import export_file_docs

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

def get_line_docs(lineparts,scope,index):
    try:
     docs = [] 
     idindex,rindex,tindex,tqindex,tcindex,trindex,ttindex,ttrindex,szindex,feindex,beindex,stcountindex = find_line_indexes(scope)
     doc_keywords = {"_index":index,"_type":"_doc","cluster": lineparts[rindex], "loghost": lineparts[rindex+1], "database": lineparts[rindex+2], "verb": lineparts[rindex+3], "timestamp":lineparts[tindex]}
     if scope == 'endpoint':
      doc_keywords['endpoint'] = lineparts[rindex+4]
     tqvals= {"_id": str(lineparts[tindex])+str(lineparts[idindex])+'0',"metric": 'tq', "min":lineparts[tqindex],"avg":lineparts[tqindex+1],"max":lineparts[tqindex+2],"count":lineparts[tqindex+3],"sum":lineparts[tqindex+4]}
     tcvals= {"_id": str(lineparts[tindex])+str(lineparts[idindex])+'1',"metric": 'tc', "min":lineparts[tcindex],"avg":lineparts[tcindex+1],"max":lineparts[tcindex+2],"count":lineparts[tcindex+3],"sum":lineparts[tcindex+4]}
     trvals= {"_id": str(lineparts[tindex])+str(lineparts[idindex])+'2',"metric": 'tr', "min":lineparts[trindex],"avg":lineparts[trindex+1],"max":lineparts[trindex+2],"count":lineparts[trindex+3],"sum":lineparts[trindex+4]}
     ttvals= {"_id": str(lineparts[tindex])+str(lineparts[idindex])+'3',"metric": 'tt', "min":lineparts[ttindex],"avg":lineparts[ttindex+1],"max":lineparts[ttindex+2],"count":lineparts[ttindex+3],"sum":lineparts[ttindex+4]}
     ttrvals= {"_id": str(lineparts[tindex])+str(lineparts[idindex])+'4',"metric": 'ttr', "min":lineparts[ttrindex],"avg":lineparts[ttrindex+1],"max":lineparts[ttrindex+2],"count":lineparts[ttrindex+3],"sum":lineparts[ttrindex+4]}
     szvals= {"_id": str(lineparts[tindex])+str(lineparts[idindex])+'5',"metric": 'sz', "min":lineparts[szindex],"avg":lineparts[szindex+1],"max":lineparts[szindex+2],"count":lineparts[szindex+3],"sum":lineparts[szindex+4]}
     fevals= {"_id": str(lineparts[tindex])+str(lineparts[idindex])+'6',"metric": 'fe', "min":lineparts[feindex],"avg":lineparts[feindex+1],"max":lineparts[feindex+2],"count":lineparts[feindex+3],"sum":lineparts[feindex+4]}
     bevals= {"_id": str(lineparts[tindex])+str(lineparts[idindex])+'7',"metric": 'be', "min":lineparts[beindex],"avg":lineparts[beindex+1],"max":lineparts[beindex+2],"count":lineparts[beindex+3],"sum":lineparts[beindex+4]}
     stvals= {"_id": str(lineparts[tindex])+str(lineparts[idindex])+'8',"metric": 'st', "count_status_200":lineparts[stcountindex],"count_status_300":lineparts[stcountindex+1],"count_status_400":lineparts[stcountindex+2],"count_status_500":lineparts[stcountindex+3],"pct_fail_status":lineparts[stcountindex+4]}
     tqvals.update(doc_keywords)
     tcvals.update(doc_keywords)
     trvals.update(doc_keywords)
     ttvals.update(doc_keywords)
     ttrvals.update(doc_keywords)
     szvals.update(doc_keywords)
     fevals.update(doc_keywords)
     bevals.update(doc_keywords)
     stvals.update(doc_keywords)
     docs.append(dict(tqvals))
     docs.append(dict(tcvals))
     docs.append(dict(trvals))
     docs.append(dict(ttvals))
     docs.append(dict(ttrvals))
     docs.append(dict(szvals))
     docs.append(dict(fevals))
     docs.append(dict(bevals))
     docs.append(dict(stvals))
     return docs 
    except Exception as e:
     logging.warn("{proxydata elasticsearch exporter} Request Processing Unexpected  Error : "+str(e))
     return docs 


def execute_exportproxy(url,username,password,ssl,cert,fromtime,totime,granularity,scope,resultslocation):
   try: 
      today = datetime.date.today()
      today_string = str(today.strftime("%Y%m%d"))
      index = 'proxy_'+str(scope)+'_'+today_string
      es = es_connect(url,username,password,ssl,cert)                     
      if os.path.exists(resultslocation):
       filestart = "stats_"+str(scope)+"_by_"+str(granularity)+"_"+str(fromtime)+"_to_"+str(totime)
       for filename in os.listdir(resultslocation):
        if filename.startswith(filestart):
           ef = open(resultslocation+'/'+filename,'r')
           eflines = ef.readlines()
           filedocs = []
           for efline in eflines:
            if not 'mtime' in efline:
              eflineparts = efline.split(',') 
              filedocs = filedocs + get_line_docs(eflineparts,scope,index)
           added = export_file_docs(es,filedocs)
           logging.warn("{proxydata elasticsearch exporter} exporting from file ["+str(filename)+"] to index ["+str(index)+"] Documents added=["+str(added)+"]") 
           return True
      else:
       logging.warn("{proxydata elasticsearch exporter} resultslocation ["+str(resultslocation)+"] not found*")
       return False 
   except Exception as e:
      filestart = "stats_"+str(scope)+"_by_"+str(granularity)+"_"+str(fromtime)+"_"+str(totime)
      logging.warn("{proxydata elasticsearch exporter} Request Processing Unexpected  Error : "+str(e))
      logging.warn("{proxydata elasticsearch exporter} exporting from file ["+str(filestart)+"*]")
      return False 
