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


def find_line_indexes(datatype):
     if datatype == 'host':
      idindex = 0
      rindex = 1
      tindex = 4
      mindex = 5 
     elif datatype == 'ioqtype':
      idindex = 0
      rindex = 1
      tindex = 5
      mindex = 6 
     if datatype == 'smoosh':
      idindex = 0
      rindex = 1
      tindex = 5
      mindex = 6 
     return idindex,rindex,tindex,mindex

def get_line_docs(lineparts,datatype,index):
    try:
     docs =  []
     idindex,rindex,tindex,mindex = find_line_indexes(datatype)
     if datatype == 'host':
      doc = { "_index":index,"_type":"_doc","_id": str(lineparts[tindex])+str(lineparts[idindex]), "cluster": lineparts[rindex], "host": lineparts[rindex+1], "timestamp":lineparts[tindex],
      "count_document_writes":lineparts[mindex],"count_document_inserts":lineparts[mindex+1], "max_ioq_latency":lineparts[mindex+2],"median_ioq_latency":lineparts[mindex+3],
      "percentile_90_ioq_latency":lineparts[mindex+4],"percentile_99_ioq_latency":lineparts[mindex+5],"percentile_999_ioq_latency":lineparts[mindex+6],}
     elif datatype == 'ioqtype':
      doc = { "_index":index,"_type":"_doc","_id": str(lineparts[tindex])+str(lineparts[idindex]), "cluster": lineparts[rindex], "host": lineparts[rindex+1], "ioqtype": lineparts[rindex+2], "timestamp":lineparts[tindex],
      "count_requests":lineparts[mindex]}
     elif datatype == 'smoosh':
      doc = { "_index":index,"_type":"_doc","_id": str(lineparts[tindex])+str(lineparts[idindex]), "cluster": lineparts[rindex], "host": lineparts[rindex+1], "channel": lineparts[rindex+2], "timestamp":lineparts[tindex],
      "count_active_jobs":lineparts[mindex],"count_waiting_jobs":lineparts[mindex+1],"count_starting_jobs":lineparts[mindex+2]}
     docs.append(dict(doc))
     return docs 
    except Exception as e:
     logging.warn("{hostdata elasticsearch exporter} Request Processing Unexpected  Error : "+str(e))
     return docs 

def execute_exporthost(url,username,password,ssl,cert,fromtime,resultslocation):
   try:
      today = datetime.date.today()
      today_string = str(today.strftime("%Y%m%d")) 
      smooshfile = "smooshstats_"+str(fromtime)
      ioqtypefile = "ioqtypestats_"+str(fromtime)
      hostfile = "hoststats_"+str(fromtime)
      es = es_connect(url,username,password,ssl,cert)                     
      if os.path.exists(resultslocation):
       for filename in os.listdir(resultslocation):
        if filename.startswith(smooshfile) or filename.startswith(ioqtypefile) or filename.startswith(hostfile) :
           if filename.startswith('smoosh'):
            datatype = 'smoosh'
           elif filename.startswith('ioqtype'):
            datatype = 'ioqtype'
           elif filename.startswith('host'):
            datatype = 'host'
           index = 'couchdbstats-es-couchdbnode_'+datatype+'_'+today_string
           filedocs=[]
           ef = open(resultslocation+'/'+filename,'r')
           eflines = ef.readlines()
           for efline in eflines:
            if not 'mtime' in efline:
              eflineparts = efline.split(',') 
              filedocs = filedocs + get_line_docs(eflineparts,datatype,index)
           added = export_file_docs(es,filedocs)
           logging.warn("{hostdata elasticsearch exporter} exporting from file ["+str(filename)+"] to index ["+str(index)+"] Documents added=["+str(added)+"]")
       return True
      else:
       logging.warn("{hostdata elasticsearch exporter} resultslocation ["+str(resultslocation)+"] not found*")
       return False 
   except Exception as e:
      logging.warn("{hostdata elasticsearch exporter} Request Processing Unexpected  Error : "+str(e))
      return False 
