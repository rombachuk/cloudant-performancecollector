
# Introduction
## Release Information
This document version is aligned with Release 28
## Document Purpose
The purpose of this document is to provide a user guide for the cloudant-performancecollector tool, delivered by IBM Services. 
The tool is provided on an opensource basis, and customers are free to enhance or modify the tool in any way. Such changes may of course modify the features, options, and descriptions provided in this document.

## Intended Audience 
The intended audience for this document are IBM customers who are deploying Cloudant Local Edition Clusters, and wish to use the performancecollector features in the management of operations on their clusters.
## Commercial Clarification 
 
This document does not amend in any way existing agreed terms and conditions of service, and readers are referred to IBM client representatives for any issues concerning terms and condition of service.
## Notices 
INTERNATIONAL BUSINESS MACHINES CORPORATION PROVIDES THIS PUBLICATION "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE. Some jurisdictions do not allow disclaimer of express or implied warranties in certain transactions, therefore, this statement may not apply to you.
This information could include technical inaccuracies or typographical errors. Changes are periodically made to the information herein; these changes will be incorporated in new editions of the publication. IBM may make improvements and/or changes in the product(s) and/or the program(s) described in this publication at any time without notice.
Any references in this information to non-IBM websites are provided for convenience only and do not in any manner serve as an endorsement of those websites. The materials at those websites are not part of the materials for this IBM product and use of those websites is at your own risk.
IBM may use or distribute any of the information you provide in any way it believes appropriate without incurring any obligation to you.
IBM, the IBM logo, and ibm.com are trademarks or registered trademarks of International Business Machines Corp., registered in many jurisdictions worldwide. Other product and service names might be trademarks of IBM or other companies. A current list of IBM trademarks is available on the web at Copyright and trademark information  

#	Features Summary
##	Periodic Data Collection and Reporting 
This feature allows data to be collected from sources on running clusters and displayed on dashboards with the grafana tool using postgres as a SQL data source. 

Each row collected is stamped with the cluster-id so data from several clusters can be captured to the same postgres data source.

This feature provides statistics at a finer scope than available from the metrics dashboard which is limited to dbnode or whole-cluster. This allows the breakdown of traffic and performance response rates by database-sets, which may reflect different users/projects/tasks sharing the same cluster. 
  
Collection is supported for :  
  
* per-database metrics using haproxy log sources (proxydata collector)
* per-client metrics using haproxy log sources (clientdata collector)
* per-host and per-type metrics using metricsdb database source (metricsdbdata collector)
* per-database and per-view volume metrics using cluster dbs as data source (volume collector)

Collection frequency is controlled by cron :  
  
* haproxy,client and metricsdb sourced data are collected every minute.  
* cluster volume metrics are collected every day

Cluster-volume and proxydata collection are practical only when the number of databases is small - several thousand or less.

Clientdata collection is practical only when the number of distinct clientip addresses calling the cluster is small.

In deployments using _10k databases or more_, constant periodic collection of haproxy and cluster-volume data **_should be disabled_**. Enabling these periodic collections is too intensive on the cluster and postgres storage. 

Other collection rates and granularity are possible, but recommended only for limited-period investigative activities. See the Investigation features of this document, and the Investigation documentation.
## Problem Detection with Threshold Conditions
This feature allows problems to be detected by comparing the periodically-collected haproxy-sourced data against metric thresholds.   
  
For each per-minute collection period, event files may be produced which itemise the item and threshold-breach. Event files can be parsed by a Event Consolidation system such as `IBM Netcool Operations Insight` and processed onto event dashboards and paging systems.

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

The user can build shell scripts with these options and feed postgres and grafana. Custom schema creation and dashboard building may be required. 
 

Consult the **Investigation using Cron** documentation for further information.

## Investigation using API 

This feature is supported for proxydata.

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




