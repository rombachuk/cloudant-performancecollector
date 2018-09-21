 
#	Overview

 This feature is intended to allow detailed one-time collections using an api interaction :

* The /_api/perfagent endpoint is used to submit a job which is serviced by the cloudant-performancecollector tool.
* The api tests the credentials supplied in the job submission REST call. Invalid credentials will mean the call is rejected and the job is not submitted.
* The cloudant-performancecollector services one job at a time to limit the cpu usage overhead of performance collection and processing.
* The results are placed in JSON format by the performancecollector into the job document which can be read via the api. 
* The job is marked completed once the results are placed.
* Once the job.status='success', the response field will contain  response.stats and response.events json fields.
* Failed jobs will have status='failed' with job.info storing identified reasons.


The results provide:

* cluster performance metrics broken down by resource level and time-period.
* statistics at a finer scope than available from the metrics database
* breakdown of traffic and performance response rates by database-sets which may reflect different users/projects/tasks sharing the same cluster

Resource levels supported are:

* all (ie whole cluster)
* database
database + verb (ie reads, writes, deletes, etc)
* database,verb,endpoint where endpoint reflects grouping of requests to endpoint type  
-- _design (ddl operations)  
-- _find (all cloudantquery type calls)  
-- design/view (all map-reduce calls)  
-- documentlevel (all calls to individual docs
  
Time-Period granularity levels supported for the supplied start- and end- datetime are:

* per-minute
* per-hour
* per-day
* all (the whole report-period)

Defaults are applied if parameters are omitted in the request. These are set in a configuration file cloudant-specialapi/perfagent.conf by the specialapi operator (typically the cluster dba team).

The cloudant-performancecollector supports a wide range of options which include data exclusion lists and threshold detection. Consult **Proxydata Collection Options** for details.

Only those users listed in csapi_users file will be authorised. The REST call can use either a AuthSession cookie, or basic authentication.

# Examples
The following examples show how api calls can be used to collect data. Missing options in the parameter list ?op1=1&op2=2 mean that defaults apply.   
See the **Proxydata Collection Options** document for a detailed specification of options available, and how defaults are configured.
### Submission : specify [fromtime]

Example submission using default options but with a report timeperiod from X to X+2hours (default for end):

```  
curl -u middleamd:***   
"http://activesn.bkp.ibm.com/_api/perfagent?
fromtime=2018-01-16-22:00" -X POST  
```
Successful submitted response with document id & revision, and ok=true

```  
{"rev": "1-d19ef6e68bdaa6b22ce113e6cf78328e",   
"ok": true,	"id": "20180116210859687426"}	
```   
The document id can be inspected - it is contained within database **_apiperfagentqueue_**
 
### Submission : specify [scope,time-granularity,fromtime,totime]

Example submission using default options but with a report timeperiod from X to current time (use keywork **_now_** to specify up to current time):

```
curl -u middleamd:*** "http://activesn.bkp.ibm.com/_api/perfagent?  
scope=database&granularity=day&from=201601150000&totime=now -X POST  
```
Succesful submitted response with document id & revision, and ok=true

```
{"rev": "1-38a6ad776952d6ead4034101f25b5d0c",   
"ok": true, "id": "20180116215504573496"}	  
```  

### Submission : error handling
Example submission using an illegal parameter:

```
curl -u middleamd:*** "http://activesn.bkp.ibm.com/_api/perfagent&invalid=a" -X POST
```
The responew from the api is:

```
{"error": "Not Found"}  
``` 
If no documentid is returned then the request is not accepted.

### Results Collection
In this example the user submits a request to see the content of an earlier submission via the api and then pipes the response to the json formatter tool **jq**

```
curl -u middleamd:*** "http://activesn.bkp.ibm.com/_api/perfagent/20180116163207007124" | ./jq
```
The response from the api piped through jq is shown below. The example had scope=endpoint.
The format of the response and expected fields is described in detail in  **Proxydata Collection Options** 

```
{
  "status": "success",
  "updated": "2018-01-16 16:32:16.644002",
  "_rev": "2-7564cb298f5a2eaf915c8c904a835b94",
  "qtime": "20180116163207007124",
  "submitted": "2018-01-16 16:32:07.007124",
  "response": {
    "stats": [
      {
        "st3sum": 0,
        "szmin": 166,
        "st2avg": 200,
        "st3min": 0,
        "st4sum": 0,
...
        "st3avg": 0,
        "endpoint": "document-level",
        "database": "_api",
        "loghost": "",
        "szcount": 1,
        "trcount": 1,
        "tqmin": 15,
        "st3max": 0,
        "trsum": 29,
        "st4min": 0,
        "st2sum": 200,
        "st2count": 1,
        "st4avg": 0,
        "tqcount": 1,
        "st5count": 0
      },
      {
        "st3sum": 0,
        "szmin": 180,
        "st2avg": 200,
        "st3min": 0,
        "st4sum": 1209,
        "st5max": 0,
        "st4count": 3,
        "tqsum": 88,
        "tqavg": 14.7,
        "ttrmax": 16,
        "mtime": "2018011616",
        "szsum": 2592,
...
        "endpoint": "document-level",
        "database": "_api",
        "loghost": "",
        "szcount": 6,
        "trcount": 6,
        "tqmin": 14,
        "st3max": 0,
        "trsum": 70,
        "st4min": 401,
        "st2sum": 600,
        "st2count": 3,
        "st4avg": 403,
        "tqcount": 6,
        "st5count": 0
      },
....
       "trsum": -44,
        "st4min": 400,
        "st2sum": 0,
        "st2count": 0,
        "st4avg": 400.2,
        "tqcount": 44,
        "st5count": 0
      }
    ],
    "events": [
      {
        "eventtime": "2018011616",
        "resource": "Database=_session,Verb=DELETE,Endpoint=none",
        "eventdetails":"AlertKey=Threshold Breach,  
        Condition=[stfailpct>=0],Value=[2],Qualifier=[ttcount>1],QValue=[83]"
      }
    ]
  },
  "requester": "middleamd",
  "_id": "20180116163207007124",
  "completed": "2018-01-16 16:32:16.644002",
  "opts": {
    "outputformat": "json",
    "inputlogfile": "/var/log/haproxy.log",
    "loghost": "",
    "certverif": false,
    "connectioninfo": "/opt/cloudant-specialapi/perfagent_connection.info",
    "performercount": "10",
    "totime": "201801161632",
    "granularity": "hour",
    "resultslocation": "/opt/cloudant-specialapi/perfagent_results",
    "scope": "endpoint",
    "eventsexclusionsfile": "/opt/cloudant-specialapi/perfagent_events_exclusions.info",
    "fromtime": "201801161432",
    "thresholdsfile": "/opt/cloudant-specialapi/perfagent_thresholds.info",
    "statsexclusionsfile": "/opt/cloudant-specialapi/perfagent_stats_exclusions.info"
  }
}

