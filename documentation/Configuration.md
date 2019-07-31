 
# Overview

_**This document revision applies to release `30.0.0` and after.**_ 

The performancecollector is used to collect metrics every minute and every day.  
The periods are controlled by the crontab of `root`.  

The file `resources/export/<target>/templates/crontab_example` are provided as a template, where <target> is one of `postgres,elasticsearch,multiple`.

The major items to configure are :

* crontab file for `root` 
* cluster access details (eg with password updates)
* target access details (eg with password updates)

You may find after operating the collection for some time that you want to ignore data or thresholds and you can do this via exclusions and the thresholds file.


# Configuration Items

### Proxy data format

This is relevant to proxydata and clientdata collectors.

This is achieved through configuration file **resources/collect/configuration/perfagent-collect.conf**

Align the base index in this file with the Number of logline tokens (fields) set up in the haproxy.log files (usually either 17 or 19), for example with no captures in the haproxy.log we would have :

base_index 17

### Cluster access details

This is relevant to metricsdb and volumedb collectors.

This is achieved through configuration file **resources/collect/configuration/perfagent_connection.info**

Set up the access url and credentials for the cluster.  
  
```
clusterurl      http://activesn.bkp.ibm.com  
admincredentials    bWlk********3MHJk    
```
  
The clusterurl should be the vip of the cloudant local cluster.  
The admin credentials shoud be a base64encoding of the string user:password where the user is a cluster admin user.

### Export target access details (postgres)

***for Postgres target : Configuration data export - step1 (resources/export/postgres/configuration/perfagent\_pg_db.info)***

Set up the hostname:db string for use by the postgres loading scripts.
The expected format is postgreshost:db . The :  is important

```
ldap.bkp.ibm.com:postgres    
```   
* The postgres host would be `ldap.bkp.ibm.com`.
* The postgres database would be `postgres` (postgres is the default).  

***for Postgres target : Configuration data export - step2 (resources/export/postgres/configuration/perfagent\_pg_credentials.info)*** 

Set up the pguser:pgpassword as a base64 string for use by the postgres loading scripts. You can do this from the shell using 

```
$ echo cloudant:passw0rd | base64 > perfagent_pg_credentials.info    
```   
* The postgres user would be `cloudant`.
* The postgres password would be `passw0rd` 
* In the above example you would see the following contents in the file. 

`Y2xvdWRhbnQ6cGFzc3cwcmQK`

### Export target access details (elasticsearch)

***Elasticsearch target : Configuration data export - step1 (resources/export/elasticsearch/configuration/perfagent\_es_connection.info)***

```
url		https://my_es_host.databases.appdomain.cloud:31739	
ssl		enabled
certificate	/opt/cloudant-performancecollector/resources/export/elasticsearch/configuration/certificates/ca.pem
credentials	aWJt***g==	
```
* The url should be the url of the elasticsearch target. Include http/https and port.
* if ssl is enabled then the connection will match against the certificate value using TLS
* The certificate identifies the CAcert file to be used in TLS verification
* The access credentials shoud be a base64encoding of the string `user:password`   

You can do generate the `credentials` string from the command prompt eg

```
[root@cl11c74lb1 configuration]# echo cloudant:passw0rd | base64
Y2xvdWRhbnQ6cGFzc3cwcmQK 
```   

***Elasticsearch target : Configuration data export - step2 (resources/export/elasticsearch/configuration/certificates)***

Place your CAcert certificate at this location. You must match it with the filename identified in step1 above. 

### Proxydata collector exclusions  

This is relevant to proxydata collectors.

This is achieved through configuration file **resources/collect/configuration/perfagent\_stats\_exclusions.info**

Proxy data is delineated by database that is accessed.

Some data can be excluded from collection to avoid distorting 'avg' statistics or for other reasons.

Data from defined clientips can be excluded eg data from backup cluster ip addresses.  

See **Proxydata Collection Options** for more details.

### Clientdata collector exclusions  

This is relevant to clientdata collectors.

This is achieved through configuration file **resources/collect/configuration/clientdata\_stats\_exclusions.info**

Client data is delineated by client that is making the call.

Some data can be excluded from collection to avoid distorting 'avg' statistics or for other reasons.

See **Proxydata Collection Options** for more details. 

The syntax for clientdata exclusions is the same as for proxydata. So you can exclude data for specific database rows even though the clientdata collector does not capture the database-level counts.

### Event Detection exclusions  

This is relevant to proxydata collectors.

This is achieved through configuration file **resources/collect/configuration/perfagent\_events\_exclusions.info**

Some proxy data lines data can be excluded from event-sensing to avoid unwanted repeated events or other reasons.

Use this file to define what you wish to ignore. 
See **Proxydata Collection Options** for more details. 

### Event Condition Thresholds
This is relevant to proxydata collectors.

This is achieved through configuration file **resources/collect/configuration/perfagent\_events\_thresholds.info**

Use this file to define what you wish to signal as the limit for eventing. See the configuration documentation for more details.


### Crontab configuration

Once the software is newly deployed, then the root user cron must be configured for periodic operation. It is recommended that :

* `proxydata_every_minute verb` is enabled on each load-balancer (linked to local haproxy.log file)  
* `clientdata_every_minute verb` is enabled on each load-balancer (linked to local haproxy.log file)  
* `proxydata_every_minute endpoint` is **disabled** on each load-balancer (linked to local haproxy.log file) and used only for investigative work
* `metricsdbdata_every_minute entry` is enabled on _just one_ load-balancer (using the vip cluster address means it works even when it is not the primary)  
* `volumedata_every_day` is enabled on _just one_ load-balancer (using the vip cluster address means it works even when it is not the primary)

#### Example

The template file **crontab_example** provided has the following content :

```
* * * * * /opt/cloudant-performancecollector/resources/export/<target>/scripts/continuous/proxydata_every_minute.sh verb 2 1 > /dev/null 2>&1
* * * * * /opt/cloudant-performancecollector/resources/export/<target>/scripts/continuous/clientdata_every_minute.sh verb 2 1 > /dev/null 2>&1
#* * * * * /opt/cloudant-performancecollector/resources/export/<target>/scripts/continuous/proxydata_every_minute.sh endpoint 2 1  > /dev/null 2>&1
* * * * * /opt/cloudant-performancecollector/resources/export/<target>/scripts/continuous/metricsdbdata_every_minute.sh > /dev/null 2>&1
30 11 * * * /opt/cloudant-performancecollector/resources/export/<target>/scripts/continuous/volumedata_every_day.sh  > /dev/null 2>&1
```
The lines can be copied to root's crontab, and the following adjustments made :

* change `30 11` to the time of day you want volumedata collected


##	Cron Operation Script Details  

It is convenient to set up a regular cronscript to capture data every minute, and display it on a dashboard.

Four scripts are provided :- 
 
* proxydata\_every\_minute.sh  
-- 	processes data in haproxy.log files
* clientdata\_every\_minute.sh  
-- 	processes data in haproxy.log files  
* metricsdbdata\_every\_minute.sh  
-- reads data from cluster (metricsdb) via REST 
* volumedata\_every\_day.sh  
-- reads data from cluster (every db) via REST 


### proxydata script (haproxy data)
The script is used to populate one of `[database_stats | verb_stats | endpoint_stats]` tables in postgres, depending on the scope parameter (\$1) used. It can be called several times to fill in the different scope levels, as required.

***Options*** 

The script uses the command line option and requires parameters for:-  

*	($1) scope of stats capture - one of [all | database | verb | endpoint | document]
*	($2) start-period for stats collection, set as (now - E) minutes
*	($3) end-period for stats collection, set as (now - S) minutes

The start-period is typically 2, and the end-period is typically 1. This means the data is 1 minute old at time of collection.

***Characteristics***

The script has the following characteristics:  

*	runs in crontab for root on the server where perfagent is installed.   
*	access to the haproxy logfile is required.   
-- 	If the perfagent is not on a Cloudant load-balancer, then rsyslog must be used to continually copy the haproxy.log file to the server that the perfagent runs on. Amend the following line to point to your specific logfile name and location if it is different from below...

```
tail -n 500000 /var/log/haproxy.log | grep $fromgrep | gzip > $logfile
```

*	The script grabs 500000 last lines of the log file and matches the start-period minute. 
*	a command-line execution for perfagent using csv option is invoked on the resulting matches. 
*	writes the csv output content to the 'postgres' database as user 'cloudant' on hostname given by parameter $4 (can be changed by editing the perfagent\_every\_minute.sh file)
*	deletes temporary files and the results once it has loaded
*	takes about 2 seconds to execute where 15000 lines/minute are present

The script has been optimised to run as quickly as possible, so that the collector can run on both production load-balancers. However, load-balancer cpus can be freed if rsyslog is used to pipe the haproxy.log file to another server. 

### clientdata script (haproxy data)

This runs in the same way as the proxydata script, but aggregates to client level, rather than database.



### metricsdbdata script (cluster metricsdb database)
The script is used to populate the following performance data targets: 
 
* host\_stats  
* smoosh\_stats  
* ioqtype\_stats  

This script is designed to collect the 'latest' information from the cluster, and be run every minute. 

The metrics database has a 1 minute lag in timestamping its data. This can lead to lags between compaction and proxydata timestamps, and data point gaps in dashboards.


### volumedata script (cluster metadata)
The script is used to populate the following performance data targets: 
 
* db\_stats  
* view\_stats 

This script is designed to collect the 'latest' information from the cluster, and be run every day. 

 
