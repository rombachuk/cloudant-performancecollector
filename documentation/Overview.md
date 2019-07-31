
# Introduction
## Release Information
This document version is aligned with Release 30
## Document Purpose
The purpose of this document is to provide a user guide for the couchdb cloudant-performancecollector tool, delivered as an open source tool. 
The tool is provided on an opensource basis, and users are free to enhance or modify the tool in any way. Such changes may of course modify the features, options, and descriptions provided in this document.

## Intended Audience 
The intended audience for this document are users who are deploying CouchDB clusters, and wish to use the performancecollector features in the management of operations on their clusters.

## Notices 


#	Features Summary
##	Periodic Data Collection & Reporting  
This feature allows metrics data to be collected from sources on running clusters of :

* CouchDB 2.+ with haproxy deployed as a load-balancer
* Cloudant Local Edition 1.1 which includes CouchDB 2.0

and exported to one of, or both of :

* postgres database
* elasticsearch database

Companion dashboards (using Grafana and/or Kibana) are available to visualise the data collected.

###	Collection 

Each row collected is stamped with the cluster-id so data from several clusters can be exported to the same  data source, and allows the performance of different clusters to be evaluated independently or compared.

This deliverable provides statistics at a finer scope than available from :

* Cloudant Local 1.1 metrics dashboard, which is limited to aggregations at dbnode-level or at whole-cluster
* CouchDB futon dashboard

It allows the breakdown of traffic and performance response rates by database-sets, which may reflect different users/projects/tasks sharing the same cluster, or be distributed across several clusters. 
  
Collection is supported for :  
  
* per-database/verb/endpoint metrics using haproxy log sources (proxydata collector)
* per-database/verb/endpoint/query-body metrics using haproxy log sources (bodydata collector)
* per-client/database/verb metrics using haproxy log sources (clientdata collector)
* per-host and per-type metrics using metricsdb database source available in Cloudant Local 1.1 (metricsdbdata collector)
* per-database and per-view volume metrics using cluster dbs as data source (volume collector)

Collection frequency is controlled by cron :  
  
* haproxy,client and metricsdb sourced data are collected every minute.  
* cluster volume metrics are best collected every day (or potentially per hour for lowcount clusters (100-200 dbs+views))
* bodydata metrics are recommended for one-shot collection only, not continuous schemes, as they generate a large number of terms. Bodydata metrics can be processed for per-minute or per-second granularity.

Aggregation processing is :

* proxy,client and bodydata are pre-aggregated using python-pandas into min/max/avg/sum/count buckets
* metricdbdata is collected from the Cloudant Local metricsdb which collects from CouchDB stats sources and pre-aggregated per minute
* volumedata is collected from CouchDB db endpoints and is not aggregated

Cluster-volume and proxydata collection are practical only when the number of databases is small - several thousand or less.

Clientdata collection is practical only when the number of distinct clientip addresses calling the cluster is small.

In deployments using _10k databases or more_, constant periodic collection of haproxy and cluster-volume data **_should be disabled_**. Enabling these periodic collections is too intensive on the cluster and database storage. 

Other collection rates and granularity are possible, but recommended only for limited-period investigative activities. See the Investigation features of this document, and the Investigation documentation.

### Export

Export can be configured for one or more sources. The tool generates a common collection file and uses that to feed one or more export pipelines. This limits the collection cpu overhead. 

Export can be executed on a one-time or a continuous basis (ie after every collect). Scripts are provided to support each mode of operation.

Export is supported for:

* postgres
* elasticsearch

### Reporting (Visualisation)

The companion opensource deliverable 'Cloudant Performance Collector Dashboards' is provided to provide a default set of dashboards which work with the exported data. 

* Grafana dashboards are available for : postgres, elasticsearch 

* Kibana dashboards are available for : elasticsearch


## Problem Detection with Threshold Conditions (proxydata only)
This feature allows problems to be detected by comparing the periodically-collected haproxy-sourced data against metric thresholds.   
  
For each per-minute collection period, event files may be produced which itemise the item and threshold-breach. Event files can be parsed by a Event Consolidation system  and processed onto event dashboards and paging systems.

Clear condition event file lines are not produced, so the event system must detect when a threshold is no longer breached.

Threshold conditions are defined in a file. Exclusions can be used to ignore conditions which are frequent and/or do not require action.

The performancecollector supports:  
  
* multiple threshold checks against any haproxy-derived metric
* multiple exclusion conditions either for metric or item
* absolute thresholds not adaptive thresholds

This feature is supported for the proxydata collector. 
It allows event files to be produced if the collected values breach a threshold.

Thresholds are defined in json format and support criteria based on combinations of :

* resource value eg verb=GET, database=phe.*
* metric value eg travg > 50
* qualifiers eg only fire when trcount > 20

    
## Investigation using cron 

This feature allows more detailed/granular metrics to be collected for short periods. 

This can mean :

* increasing the resource levels of metrics from per-database to per-database-endpoint (proxydata or clientdata)
* investigating using bodylevel onetime scripts (bodydata) and Traffic Detail dashboards
* increasing the collection rate from per-day to per-hour or per-minute (volumedata)

Dashboards are available to support these types of investigation.
 
The performancecollector supports a powerful set of options to process investigative collections of haproxy data at various resource levels (scope) and time-rollups (granularity).   

The user can build shell scripts with these options and feed their export-target. Custom schema/index/template creation and dashboard building may well be required. 
 

Consult the **Investigation using Cron** documentation for further information.

## Investigation using API 

This feature is supported for proxydata, and requires installation and operation of the cloudant-specialapi tool which is also available from this github user site.

This feature is intended to allow detailed one-time collections using an api call :  

* user makes a POST request to the cluster \_api/perfagent endpoint with the required options
* successful submission results in a returned documentid with status 'submitted'
* on completion of the collection, the status is marked 'completed'
* The results are placed in JSON format by the performancecollector into the job document which can be read via the api. The job is marked completed once the results are placed. 

Consult the **Investigation using API** and **ProxyData Collection Options** for details.

Requests are processed through a queue to prevent mass-parallel collection and a cpu hit on the load-balancer. 
 
Large json results sets are possible if a endpoint-scope per-minute collection for a large start and stop time are invoked: especially when there are large numbers of databases on the cluster.

Care should be taken to avoid these calls.

It is recommended that the \_api/perfagent endpoint is disabled in the _specialapi_ outside of investigation processes. This protects the cluster workloads from accidental large results sets.

Consult the **Investigation using API** documentation for further information.




