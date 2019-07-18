import logging
from elasticsearch import Elasticsearch
from ssl import create_default_context

def es_connect(url,username,password,ssl,cert):
    try: 
     urlparts=url.split(':')
     if len(urlparts) == 3:
      scheme = urlparts[0]
      host = urlparts[1][2:]
      port = urlparts[2]
      if ssl == "enabled" and scheme == "https":
       context=create_default_context(cafile=cert)
       es = Elasticsearch( [host],
          http_auth=(username, password),
          scheme="https",
          port=port,
          ssl_context=context) 
       return es
      elif ssl == "disabled" and scheme == "http":
       es = Elasticsearch( [host],
          http_auth=(username, password),
          scheme="http",
          port=port)
       return es
      else:
       return None 
     else:
      return None
    except Exception as e:
      logging.warn("{elasticsearch exporter} Request Processing Unexpected  Error : "+str(e))
      return None 
