 
#	Overview

The user or application submits a job request to the \_api/perfagent endpoint for haproxy-data metrics collection :  

* processing of lines falling within a timeperiod within a specified logfile
* rollup of stats to a scope, the resource-level within the cluster
* rollup of stats to a granularity in time
* detection of threshold breaches of stats matched against threshold rules, defined in a file on the api's server  

The user or application then polls the api for a result using the id returned from the accepted submission.

Once the job.status='success', the response field will contain  response.stats and response.events json fields.  

Failed jobs will have status='failed' with job.info storing identified reasons.




# Job Options
Options are supplied as html parameters in the API and as python parameters in the command-line/cron scripts. 

If parameters are omitted, a default value is used, which is set in  `/opt/cloudant-performancecollector/perfagent.conf`

This section shows the long and short form of each option, and the standard default. Datetime parameters can be specified up to minute granularity.

### totime 

* longform     `totime`
* shortform    `t`	
* default      `now`
* format		  `YYYYMMDDHH24MI` or `now`  

```
You can use the following separators which are ignored :-/_
eg 2018-01-16_12:00 is ok
special value 'now' is allowed
```

### fromtime 

* longform     `fromtime`
* shortform    `f`	
* default      `now-2hour`
* format		  `YYYYMMDDHH24MI`  

```
You can use the following separators which are ignored :-/_
eg 2018-01-16_12:00 is ok
```

### scope 

* longform     `scope`
* shortform    `s`	
* default      `verb`
* allowed		  `all,database,verb,endpoint`  

```
Defines increasingly detailed scope for rollup which also increases the number of stats returned. 
Note that:
verb means [database,verb]
endpoint means [database,verb,endpoint]
```
### granularity 

* longform     `granularity`
* shortform    `g`	
* default      `hour`
* allowed		  `all,day,hour,minute`  

```
Defines timescope for rollup - more granular the more results.
```

### outputformat 

* longform     `outputformat`
* shortform    `O`	
* default      `json` for api, `csv` for cron
* allowed		  `json,csv`  

```
Using csv for an api call will result in files on the server. 
Operations teams wil have to retrieve these. 
Not recommended to change defaults.
```
### logfilehost 

* longform     `logfilehost`
* shortform    `H`	
* default      `no default`
* allowed		  `identity of load-balancer hostname`  

```
This parameter is used to tag stats from each of the two load-balancer source hosts.   
The dashboard then sums the data and so shows the total from both load-balancers.  

Use if capturing data from both primary and secondary load-balancers: only relevant in periodic collection.   
For adhoc, api or short-period collections, the active lb is likely to be constant.
```
### inputlogfile 

* longform     `inputlogfile `
* shortform    `L`	
* default      `/var/log/haproxy.log`
* allowed		  `name of haproxy file`  

```
This parameter is used to indicate the file containing proxy data.
```

### certverif 

* longform     `certverif `
* shortform    `none`	
* default      `False`
* allowed		  `True,False`  

```
Whether to verify certificates in https connection to cluster. 
If True then the default_requests_ca_bundle entry is used as the bundle file 
(default is /opt/cloudant-performancecollector/ca.pem)
```

### connectioninfo 

* longform     `connectioninfo `
* shortform    `x`	
* default      `/opt/cloudant-performancecollector/perfagent_connection.info`
* allowed		  `name of connection info file`  

```
How the queue processor should login to the cluster to save results.
(default is /opt/cloudant-performancecollector/ca.pem)
```
### resultslocation 

* longform     `resultslocation `
* shortform    `R`	
* default      `/opt/cloudant-performancecollector/perfagent_results`
* allowed		  `name of results directory`  

```
Directory to place results files if outputformat is csv. Used only by cron, not the api.
```
### thresholdsfile 

* longform     `thresholdsfile `
* shortform    `T`	
* default      `/opt/cloudant-performancecollector/perfagent_thresholds.info`
* allowed		  `file containing thresholds to be tested`  

```
File used to define threshold conditions to be tested after stats are built.
Test if resource-level is true and stat meets criteria and qualifier meets criteria.
Use qualifier to ignore low traffic rows.
```

### eventsexclusionsfile 

* longform     `eventsexclusionsfile `
* shortform    `E`	
* default      `/opt/cloudant-performancecollector/perfagent_event_exclusions.info`
* allowed		  `file containing criteria to ignore proxydata lines in events collection`  

```
Filter criteria for ignoring stats lines for event detection.
Multiple criteria can be defined. 
Within each line, criteria are AND'd
Within the files, the lines are OR'd
```

### statsexclusionsfile 

* longform     `statsexclusionsfile `
* shortform    `E`	
* default      `/opt/cloudant-performancecollector/perfagent_stats_exclusions.info`
* allowed		  `file containing criteria to ignore proxydata lines in stats collection`  

```
Filter criteria for ignoring stats lines for event detection.
Multiple criteria can be defined. 
Within each line, criteria are AND'd
Within the files, the lines are OR'd
```
# Job Results Format
The job document is returned as json.

This section describes the result fields returned. 

### _id 

* allowed `set as submissiontime down to microeconds`
* usage  `cloudant unique id for document`

```
returned as id field of submission response.
```
### _rev 

* allowed `set by cloudant`
* usage  `cloudant revision`

```
returned as id field of submission response.
```

### requester 

* allowed `set by api`
* usage  `useraccount of job submitter`

```
for api - extracted from cookie or from basicauth header
```
### status 

* allowed `submiited,processing,failed,success`
* usage  `marker of progress for operational queue`

```
for api - queue only runs entries marked submitted - 
so updating the status to failed or canceled will drop it from the queue
```
### info 

* allowed `set by cloudant-performancecollector`
* usage  `failure reason`

```
for api - may not be present in json if success
```
### qtime 

* allowed `set by cloudant-performancecollector`
* usage  `time of submission in epoch`

```
used to order queue, so smallest qtime goes first
```
### submitted 

* allowed `set by cloudant-performancecollector`
* usage  `time of submission in human readbale format`

```
pretty format - submissiontime
```

### updated 

* allowed `set by cloudant-performancecollector`
* usage  `time of last update in human readbale format`

```
pretty format - updatetime - updated during life of job, =completed time once completed
```

### completed 

* allowed `set by cloudant-performancecollector`
* usage  `time of completion in human readbale format`

```
pretty format -  success or fail time
```
	
### opts 

* allowed `set by cloudant-performancecollector`
* usage  `list of the options submitted to job`

```
if options are omitted from request.params string, then defaults apply, and those used are listed.
```

### response.statsfile (csv option only)

* allowed `set by cloudant-performancecollector`
* usage  `name of file on api-server which has the stats`

```
csv option only 
```

### response.eventsfile (csv option only)

* allowed `set by cloudant-performancecollector`
* usage  `name of file on api-server which has the events`

```
csv option only 
```

### response.stats (json option only - api)

* allowed `set by cloudant-performancecollector`
* usage  `array of stats entries`

```
each entry has 
{resource-level,mtime, metrics values}
mtime is the rollup in time
resource-level will be at scope level.
```
See section **Metrics** for list of expected metrics.

### response.events (json option only - api)

* allowed `set by cloudant-performancecollector`
* usage  `array of events entries`

```
each having
[eventtime,eventresource,eventdetails]	outputformat=json
Use these to generate events. They are evaluated each job independently. 

They do not appear as clear if cleared since last job ie no check of previous run is done.
```


# Metrics Supported
For metrics, a set of values are calculated in the rollup, usually min/avg/max/count/sum.
The following measurements are supported :

### tq : client send time (ms)

* aggregations `min,avg,max,count,sum`
* description  `Time spent by client sending request to cloudant`

```
Can reflect a large document being submitted. Large request body.  
Measure of network issues between application client tier and cloudant. 
These values are always high for _changes endpoints since long-polling is in operation. 
Default is to exclude these rows to avoid stats distortion.
```

### tr : cloudant process time (ms)

* aggregations `min,avg,max,count,sum`
* description  `Time in ms spent being processed by cloudant engine up to point of first byte being printed back`

```
Query processing time. Key measure of view speed. 
Full document scans can occur if keys are wide as in equivalent SQL cases.
```
### ttr : (tt-tr) end-to-end process time, excluding cloudant processing (ms)

* aggregations `min,avg,max,count,sum`
* description  `Time in ms not spent in cloudant processing`

```
Useful in capturing large results sets.
Since this is the time spent printing back the result to the client, after first byte.
```
### tt : end-to-end process time, including cloudant processing (ms)

* aggregations `min,avg,max,count,sum`
* description  `Total time receiving, processing and printing back response.`  
  
```
Useful in capturing either large results set or slow queries/inserts.
```
### sz : size of response (bytes)

* aggregations `min,avg,max,count,sum`
* description  `Size of response`

```
Useful in capturing large results sets.
```
### st2 : successful REST calls 2XX

* aggregations `min,avg,max,count,sum`
* description  `response status in range 2**`

```
Successful calls. 
count is measure of successful traffic	
avg is of questionable value. 
Use as success counter, and qualifier for thresholds.
```
### st3 : failed REST calls reason 3XX

* aggregations `min,avg,max,count,sum`
* description  `response status in range 3**`

```
Failed calls. 
count is measure of failed traffic of redirect errors
avg is of questionable value.
use as failure counter, and qualifier for thresholds. 
usually 0
```
### st4 : failed REST calls reason 4XX

* aggregations `min,avg,max,count,sum`
* description  `response status in range 4**`

```
Failed calls. 
count is measure of failed traffic of errors caused by rejected calls 
avg is of questionable value.
use as failure counter, and qualifier for thresholds. 
```
### st5 : failed REST calls reason 5XX

* aggregations `min,avg,max,count,sum`
* description  `response status in range 5**`

```
Failed calls. 
count is measure of failed traffic of server-side errors
avg is of questionable value.
use as failure counter, and qualifier for thresholds.
```
### stfailpct : failed REST calls percentage

* aggregations `min,avg,max,count,sum`
* description  `Percentage failure rate`

```
Key effectiveness measure for this resource-level.
```
# Data Exclusions
Data exclusions are defined in a file on the server :

*  perfagent\_stats\_exclusions.info (proxydata collector)
*  clientdata\_stats\_exclusions.info (clientdata collector)

### Examples
```
{"verb":"GET","endpoint":"_changes"}
{"verb":"GET","endpoint":"none"}
{"clientip":"192.168.254.68"}

```

The effect of the example is to exclude from metrics proxy.log entries matching :

```
IF verb='GET' and endpoint='_changes' OR  
IF verb='GET' and endpoint='none' OR 
IF clientip = '192.168.254.68'
```

### Notes

1) If there is a deeper scope present then it applies to all lines matching the condition shown.  

2) Use clientip to ignore data from specific REST clients. You can use the clientdata collector to ensure data from all clients is still collected. It has a separate exclusion file.

3) .* is the wildcard operator (regex logic)

4) You can use exclusions in investigative work to collect data from a narrow target



# Event Thresholds
Event thresholds are defined in a file on the server (perfagent_thresholds.info)

### Examples
```
{"database":"_session.*","verb":"DELETE","metric":"stfailpct","operator":">=","limit":"0",  
"qualifier":"ttcount","qoperator":">","qlimit":"1"}
{"metric":"travg","operator":">=","limit":"90","qualifier":"ttcount","qoperator":">","qlimit":"4"}
```

The effect of the example is to generate events for any stats lines matching :

```
IF database='_session.*' and verb='DELETE' and stfailpct>=0 AND ttcount>1 OR  
if travg>90 and ttcount>4
```

If there is a deeper scope present then it applies to all lines matching the condition shown.  

So if stats exist for 

```
database:_session,verb=DELETE,endpoint=none  
database:_session,verb=DELETE,endpoint=something
```
then events are generated for both rows  

.* is the wildcard operator (regex logic)

###  Exclusions
Prevent events you dont want to see by setting an **exclusion line** in perfagent_exclusions.info  
For example `{"verb":"GET","endpoint":"_local"}`
will not generate any events for stats lines that are GET on _local endpoints (for any database)
