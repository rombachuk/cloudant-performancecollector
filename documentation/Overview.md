
# Introduction
## Release Information
This document version is aligned with Release 26.0.0
## Document Purpose
The purpose of this document is to provide a user guide for the cloudant-specialapi tool, delivered by IBM Services. 
The tool is provided on an opensource basis, and customers are free to enhance or modify the tool in any way. Such changes may of course modify the features, options, and descriptions provided in this document.
Installation instructions and guidance for integration with monitoring & alerting subsystems in the customer's deployment are covered in other documents
## Intended Audience 
The intended audience for this document are IBM customers who are deploying Cloudant Local Edition Clusters, and wish to use the specialapi features in the management of operations on their clusters.
## Commercial Clarification 
 
This document does not amend in any way existing agreed terms and conditions of service, and readers are referred to IBM client representatives for any issues concerning terms and condition of service.
## Notices 
INTERNATIONAL BUSINESS MACHINES CORPORATION PROVIDES THIS PUBLICATION "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE. Some jurisdictions do not allow disclaimer of express or implied warranties in certain transactions, therefore, this statement may not apply to you.
This information could include technical inaccuracies or typographical errors. Changes are periodically made to the information herein; these changes will be incorporated in new editions of the publication. IBM may make improvements and/or changes in the product(s) and/or the program(s) described in this publication at any time without notice.
Any references in this information to non-IBM websites are provided for convenience only and do not in any manner serve as an endorsement of those websites. The materials at those websites are not part of the materials for this IBM product and use of those websites is at your own risk.
IBM may use or distribute any of the information you provide in any way it believes appropriate without incurring any obligation to you.
IBM, the IBM logo, and ibm.com are trademarks or registered trademarks of International Business Machines Corp., registered in many jurisdictions worldwide. Other product and service names might be trademarks of IBM or other companies. A current list of IBM trademarks is available on the web at Copyright and trademark information  

#	Features Summary
##	Database Operations (_api/managedb)
This feature is intended to allow temporary 'elevated' privileges for database level operations. This allows users to create and delete databases, but without being granted '_admin' and 'server_admin' privilege. As a result, users can be prevented from seeing database content for sets of databases on a cluster that they share with other users.  
  
The managedb component supports:  
  
* creation of database
* deletion of database
* reading database endpoint  
  
for users who do not have '_admin' and 'server_admin' privilege on the cluster.  

The user makes REST calls to the cluster _api/managedb endpoint to achieve these operations.
Only those users listed in csapi_users file will be authorised.  
  
The REST call can use either a AuthSession cookie, or basic authentication.
  
The API will test the credentials supplied in the REST call against the cluster cluster-port authentication scheme. Invalid credentials at point of test will mean the call is rejected.  
  
Databases are created with members.names = request-username so that the database is read-write to the requesting user, and not world-open to anonymous requests.
## Design Document Operations via Operational Queue (_api/migrate)
This feature is intended to ensure create, update and delete operations on design-documents are processed as an operational queue, which executes in series and so limits the view_update and view_compact volumes on the cluster.   
  
For updates, the 'move and shift' technique is used, which ensures that reads with update=true or stale=false (default settings) will not block during the update process.  

The migrate component supports:  
  
* submission of create/update job to the queue, returning jobid, if accepted
* submission of delete job to the queue, returning jobid if accepted
* reading status of job, using a jobid
* deletion of designdocument 
  
The feature can be used by users who do not have 'admin' privilege to a database they are submitting the job for. The api temporarily elevates their privilege. This allows the blocking of design-doc operations via the direct Cloudant api, preventing cluster overload through high numbers of parallel view updates.  
  
The user makes REST calls to the cluster _api/migrate endpoint to achieve these operations.  

Only those users listed in csapi_users file will be authorised.  
  
The REST call can use either a AuthSession cookie, or basic authentication.  

The API will test the credentials supplied in the REST call against the cluster cluster-port authentication scheme. Invalid credentials at point of test will mean the call is rejected.  

## Performance Metrics Collection via Operational Queue (_api/perfagent)
This feature is intended to provide cluster performance metrics broken down by resource level and time-period. This provides statistics at a finer scope than available from the metrics database which is limited to dbnode or whole-cluster. This allows the breakdown of traffic and performance response rates by database-sets, which may reflect different users/projects/tasks sharing the same cluster.  

Resource levels supported are:  
  
* all (ie whole cluster)
* database
* database + verb (ie reads, writes, deletes, etc)
* database,verb,endpoint, where endpoint reflects grouping of requests to endpoint type  
-- _design (ddl operations)   
-- 	_find (all cloudantquery type calls)  
--	design/view (all map-reduce calls)  
--	documentlevel (all calls to individual docs)  
--	etc  
*	database,verb,endpoint,document  
 (ie each distinct endpoint counted separate, including every individual document - only use sparingly since it often creates many rows)  
  
Time-Period granularity levels supported are:  
  
* minute, hour, day, all (the whole report-period)  
  
The component processes statistics by inspecting log files generated in the current active haproxy.  
  
Statistics reflect the content recorded by that proxy. If a proxy changeover has occurred in the report period requested, then the result is compromised. Consult your cluster dba for a record of such events.  
  
The log-inspection method is cpu-intensive and can frequently take several minutes, so requests to the api are processed via an operational queue.  
  
The perfagent component supports:  
  
* submission of statistics collect+process job to a queue, returning job id if accepted  
* collection of status of a job and the result, using the jobid  
  
The user makes REST calls to the cluster _api/perfagent endpoint to achieve these operations.  

The component supports the detection of threshold-breach conditions within the result. Event fields are placed in the result which identify any breaches.  
  
The job is submitted with a set of options supplied as parameters to the REST call:  

* report period defined by 'fromtime' to 'totime'  
* resource level defined by 'scope'  
* time-period rollup defined by 'granularity'  
* outputformat (json or csv)  
-- If csv, then results are stored in files which are referenced in the job response field  
-- if json, then stats and events are placed in the job response field  
* location of input file to process
* connection information for the queue (allows elevated passwords to change after job submission)
  
The component also supports parameters which allow the definition of:  
    
* stats exclusions, which means log entries meeting the exclusion criteria are ignored in stats collection  
* threshold conditions with qualifiers, which are applied to stats results to look for breaches and create events in the results  
* event exclusions, which means that stats results meeting the exclusion criteria do not have events generated for them, even threshold conditions are breached
    
Defaults are applied if parameters are omitted. These are set in a configuration file by the specialapi operator (typically the cluster dba team).  
  
Only those users listed in csapi_users file will be authorised.
The REST call can use either a AuthSession cookie, or basic authentication.  

The API will test the credentials supplied in the REST call against the cluster cluster-port authentication scheme. Invalid credentials at point of test will mean the call is rejected.  

### Periodic Operation via Cron

This feature can be used on a periodic basis to generate stats for a performance management system (say every minute for the previous minute), and events for an event & incident management system. It is convenient, but not essential, to use the command-line invocation method in these cases.  
  
This separates these periodic requests from adhoc use. See <add link here> for how to integrate the command line with postgres and grafana to view realtime dashboards.

This feature can be used on an adhoc basis to gather statistics with various options to support investigation of cluster behaviour broken down by the required resource-level.

