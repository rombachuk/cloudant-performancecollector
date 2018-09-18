
# Introduction
## Release Information
This document version is aligned with Release 27
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
  
Collection is supported for:  
  
* per-database metrics using haproxy log sources
* per-host and per-type metrics using metricsdb database source
* per-database and per-view volume metrics using cluster dbs as data source  

Collection frequency is controlled by cron :  
  
* haproxy and metricsdb sourced data are collected every minute.  
* cluster volume metrics are collected every day

Cluster-volume and haproxy collection are practical only when the number of databases is small - several thousand or less.

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
    
## Investigation using cron 
 
The performancecollector supports a powerful set of options to process investigative collections of haproxy data at various resource levels (scope) and time-rollups (granularity).   

The user can build shell scripts with these options and feed postgres and grafana. Custom schema creation and dashboard building may be required. 
 
Two investigative features with example shellscripts and dashboard support are provided in the standard delivery : 
 
* per-minute metrics at database-verb-endpoint scope level.  
-- deeper than the standard database-verb level  
-- particularly useful for POST verb  
-- volume and response rates for \_find, or \_index etc.  
-- additional dashboard available (Cluster Overview by Endpoint)  

* per-minute/hour metrics for cluster volume data.  
-- more frequent than the standard per-day collection  
-- useful for compaction status tracking   
-- useful for volume build-up rates in load testing  
-- increased time granularity is supported on standard volume dashboards

Consult the **Investigation using Cron** documentation for further information.

## Investigation using API 
 
The performancecollector supports a powerful set of options to process investigative collections of haproxy data at various resource levels (scope) and time-rollups (granularity). 

These can be used to make REST-based asynchronous collection requests via the cloudant-specialapi :  

* user makes a POST request to the cluster \_api/perfagent endpoint with the required options
* successful submission results in a returned documentid with status 'submitted'
* on completion of the collection, the status is marked 'completed'
* results for metrics and threshold-events are made available as json within the document for collection from the cluster database **_apiperfagentqueue_** 

Requests are processed through a queue to prevent mass-parallel collection and a cpu hit on the load-balancer. 
 
Large json results sets are possible if a endpoint-scope per-minute collection for a large start and stop time are invoked: especially when there are large numbers of databases on the cluster.

Care should be taken to avoid these calls.

It is recommended that the \_api/perfagent endpoint is disabled in the _specialapi_ outside of investigation processes. This protects the cluster workloads from accidental large results sets.

Consult the **Investigation using API** documentation for further information.




