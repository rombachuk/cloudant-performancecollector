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
from uuid import uuid1
from es_utils import es_connect
from es_utils import export_file_docs


def find_line_indexes(datatype):
     if datatype == 'db':
      idindex = 0
      rindex = 1
      tindex = 4
      mindex = 5 
     elif datatype == 'view':
      idindex = 0
      rindex = 1
      tindex = 7
      mindex = 8 
     return idindex,rindex,tindex,mindex

def get_line_docs(lineparts,datatype,index):
    try:
     docs =  []
     idindex,rindex,tindex,mindex = find_line_indexes(datatype)
     if datatype == 'db':
      doc = { "_index":index,"_type":"_doc","_id": str(lineparts[tindex])+str(lineparts[idindex]), "cluster": lineparts[rindex], "database": lineparts[rindex+1], "timestamp":lineparts[tindex],
      "count_documents":lineparts[mindex],"count_deleted_document":lineparts[mindex+1], "size_disk":lineparts[mindex+2],"size_data":lineparts[mindex+3],
      "count_shards":lineparts[mindex+4]}
     elif datatype == 'view':
      doc = { "_index":index,"_type":"_doc","_id": uuid1(), 
              "cluster": lineparts[rindex], "database": lineparts[rindex+1], "viewdoc": lineparts[rindex+2],  "view": lineparts[rindex+3], "signature" : lineparts[rindex+4], "timestamp":lineparts[tindex],
      "size_disk":lineparts[mindex+0],"size_data":lineparts[mindex+1],"size_active":lineparts[mindex+2],"updates_pending_total":lineparts[mindex+3],
      "updates_pending_minimum":lineparts[mindex+4],"updates_pending_preferred":lineparts[mindex+5]} 
     docs.append(dict(doc))
     return docs 
    except Exception as e:
     logging.warn("{hostdata elasticsearch exporter} Request Processing Unexpected  Error : "+str(e))
     return docs 

def execute_exportvolume(url,username,password,ssl,cert,fromtime,resultslocation):
   try:
      today = datetime.date.today()
      today_string = str(today.strftime("%Y%m%d")) 
      dbfile = "dbvolumestats_"+str(fromtime)
      viewfile = "viewvolumestats_"+str(fromtime)
      es = es_connect(url,username,password,ssl,cert)                     
      if os.path.exists(resultslocation):
       for filename in os.listdir(resultslocation):
        if filename.startswith(dbfile) or filename.startswith(viewfile) :
           added=0
           if filename.startswith('db'):
            datatype = 'db'
           elif filename.startswith('view'):
            datatype = 'view'
           index = 'couchdbstats_couchdbvolume_'+datatype+'_'+today_string
           filedocs=[]
           ef = open(resultslocation+'/'+filename,'r')
           eflines = ef.readlines()
           for efline in eflines:
            if not 'mtime' in efline:
              eflineparts = efline.split(',') 
              filedocs = filedocs + get_line_docs(eflineparts,datatype,index)
           added = export_file_docs(es,filedocs)
           logging.warn("{volumedata elasticsearch exporter} exporting from file ["+str(filename)+"] to index ["+str(index)+"] Documents added=["+str(added)+"]")
       return True
      else:
       logging.warn("{hostdata elasticsearch exporter} resultslocation ["+str(resultslocation)+"] not found*")
       return False 
   except Exception as e:
      logging.warn("{hostdata elasticsearch exporter} Request Processing Unexpected  Error : "+str(e))
      return False 
