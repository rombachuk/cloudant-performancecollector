# Installing the performancecollector

## Planning your deployment

### Architecture

[architecture]: pc1.jpg

![architecture]
 
The overall architecture for operating the performancecollector on a cluster has :  

*	each load-balancer haproxy process activity to a haproxy.log file
* each cluster provides volume data via \_all\_dbs endpoint of the cluster
* cloudant-local clusters provide a metricsdb which consolidate per-minute stats data from each dbnode
*	processing of [proxy],[client],[body],[metricsdb] and [volume] data into metrics by the performancecollector
* export of metrics to a target database (postgres or elasticsearch)
*	grafana-server and/or kibana-server and connects to export target datasource(s). 
* user runs grafana/kibana dashboard on his browser which presents data from the datasource(s)

The performancecollector can be operated for a single node cluster. Typically, in these cases, haproxy is run on the same host ascouchdb/cloudant.

The performancecollector is designed for use in RHEL7 or Centos7 hosted environments. 
 
The performancecollector is most conveniently installed on the one/two load balancers of a couchdb/cloudant-local cluster
This removes the overhead of forwarding latest proxy data to another server. This can be done if it is not possible to export directly to the database target from the load-balancer nodes.

The performancecollector causes bursts of high cpu usage on one core for about 10-20 seconds per minute if REST volumes are high, and this overhead must be accounted for in loadbalancer dimensioning.   

If dedicating a core on load-balancer servers to the performance collection is not acceptable, then :  

* the performancecollector should be installed on a distinct server
* haproxy.log files can be copied to these servers from load-balancers  

The performancecollector on each load-balancer exports its results to a database:  
*  Data is blank for the standby load-balancer. 
*  On a switchover, the new active load-balancer will process data and data rows will appear.
*  Dashboards aggregate data from both load-balancers for a given switchover minute.
*  Volume & metricsdb data must be enabled on only one load-balancer. This type of collection should connect to the vip of the cluster to switch to the active load-balancer. If the load-balancer host fails entirely, then this data will not be available. The alternative is to run this collection from an independent node.

You will need to install the performancecollector on each of the clusters you wish to collect and export data for. All data is stamped with a clusterid, so it is safe to export data from several clusters to a common export target.

### Checklist

Ensure you have identified (and installed) :  

* server(s) you will install performancecollector (most commonly this will be the 2 load-balancers of a cluster)
* couchdb cluster endpoint (source of non-haproxy.log data)
* cluster type: couchdb/cloudant-local (metricsdbdata can only be enabled for Cloudant Local type couchdb clusters)
* export target database: postgres/elasticsearch 
* dashboard hub: grafana/kibana 
* connection details for cluster, export-target, and dashboard-hub
* location of haproxy.log files
* haproxy http log format (from haproxy.cfg)


## Install

### Overview

The install should be executed once all pre-requisites are complete, and connection information is available.

The install process involves installing a python module on a Linux server. This module is installed in a virtual enviroment, and is independent of the server's python global package space.

The install process backs up any previous running release to a backup directory tree, so previous setups are available for review.

The install script allows the configuration of setup data in a staging area, prior to the actual install execution. This can be adjusted afterwards, if necessary.

The install script allows the `postgres schema` or `elasticsearch templates` to be loaded to the configured export target. This should be activated only once for the first cluster exporting to this target. For subsequent clusters exporting to same target, ignore this option.

Offline and Online modes are supported. The mode is selected during the install. 
For servers isolated from the internet and the PyPI online repository, choose Offline. You will need to download the `wheelhouse.tar.gz` component of this release, and site it in the `offline` directory of the staging area.

The performancecollector is most conveniently installed and run as `root`, since haproxy is normally run as `root`

For postgres, ensure that the installation user on the performancecollector host can access the PG instance via the psql client. Export is executed using psql commands from the linux shell.

The installation may operate successfully as other linux users. Ensure access to haproxy.log is available to the user.

### Pre-Requisites

The install has several pre-requisites: 
  
* install and configuration of a export target database (postgres or elasticsearch) on a server
* install and configuration of dashboarding-hub (grafana or kibana) on a server
* for postgres export target : install and configuration of postgres client on the server you are installing the collector
* configuration of respective haproxy with http logging

#### Load Balancer haproxy configuration

***Number of logline tokens (fields)*** 

The /etc/haproxy/haproxy.cfg is used to define the log format of the haproxy.log file, and the number of fields.  

The standard haproxy configuration for Cloudant clusters does not include capture lines. This means the number of tokens per logfile line is 17.

If auditing is in place, then additional capture lines may appear. An example of capture lines for auditing is 
  
```
  capture request header Authorization len 256    
  capture cookie AuthSession= len 256  
```
The number of tokens is increased by the number of additional captures. So the haproxy.log will have 19 tokens in the above example. This number must be synchronised in a config file in the collector (see configuration).


### Configuration Key Steps

[keysteps]: pc2.jpg

![keysteps]

The diagram above highlights the key configuration steps in the installation
* configuration of haproxy log file location (step 1)
* configuration of location of haproxy log fields (aligning with haproxy.cfg settings) (step 2)
* configuration of exclusions (filters) for collection & eventing (step 3)
* configuration of cluster connection details (step 4)
* configuration of export-target connection details (step 5)
* configuration of datasources on dashboard-hub (optionally configure grafana connection details) (step 6)
* once the pipeline is tested, continuous operation is configured using cron



### Collecting software from Github

cloudant-performancecollector is released via github. Use a github client to download the release level required.

The github repository is 
`https://github.com/rombachuk/cloudant-performancecollector`

The releases option in Github shows the available releases.
Download from the site in either tar.gz or zip format, and place in a suitable directory, as `root` on the server eg `/root/software`

For `Offline` installations (no internet connection), you should also download the `wheelhouse.tar.gz` component of the release and place it in the same directory.

### 	Unpacking 
Then unpack the software with `tar xvf` or `unzip`, depending on the download format from github.

The software unpacks to the following directories :  
  
  * cloudant-performancecollector (the software to be installed)
  * documentation (markdown files documenting the package)
  * test (testing scripts for the package)
  * deploy (installation & patch scripts for the package)
  * offline (container directory for wheelhouse tar required in offline installs)
  
For `Offline` installations, copy or move the downloaded `wheelhouse.tar.gz` into the `offline` directory.

***Example***

Software release 27.0.3 is downloaded to server cl11c74lb1 directory  `/root/software/cloudant-performancecollector-27.0.2.tar.gz` and unpacked with tar as  
  
  
```  
[root@cl11c74lb1 cloudant-performancecollector-27.0.3]# pwd
/root/software/cloudant-performancecollector-27.0.3
[root@cl11c74lb1 cloudant-performancecollector-27.0.3]# ls -l
total 8
drwxrwxr-x 4 root root 4096 Sep 14 11:53 cloudant-performancecollector
drwxrwxr-x 2 root root   54 Sep 14 11:53 deploy
drwxrwxr-x 2 root root  127 Sep 14 11:53 documentation
-rw-rw-r-- 1 root root  155 Sep 14 11:53 README.md
```    

### Clean Install
This option is used when a brand new install is required, or when an existing install is to be deleted and reset.

Several steps are needed :  
  
* configure haproxy token setup 
* configure cluster access
* if postgres target: configure export target 
* if elasticsearch target: configure export target
* configure exclusions for data collection (pre-filter data)
* configure exclusions and thresholds for event-detection  - optional
* run the deploy/clean_install.sh script
* the script will prompt for online/offline mode, and target type, as it executes
* the installer will optionally build a new schema/template-set in the target :  
-- do this only once for this target and backup any existing data at the target that you need 
*(ie ignore for 2nd load balancer, and subsequent clusters exporting to this same target)* 

* configure crontab to run periodic metric collection jobs
* grafana hub: install datasources and dashboards into grafana
* kibana hub: install index into kibana


You should edit the files within the `unpacking` (or staging) area, prior to executing the clean_install script.

For example, if you have unpacked release `cloudant-performancecollector-30.0.0`to the directory `/root/software/cloudant-performancecollector-30.0.0`, then edit the files you have unpacked within directory `/root/software/cloudant-performancecollector-30.0.0/cloudant-performancecollector`


***Configuration haproxy tokens (resources/collect/configuration/perfagent-collect.conf)***  

Align the base index in this file with the index number of the 'HTTP/1.1' field in the haproxy.log files (usually either 17 or 19). Index starts at 0. For example with no captures in the haproxy.log we would have :

`base_index	17`

***Configuration cluster access (resources/collect/configuration/perfagent_connection.info)*** 

Set up the access url and credentials for the cluster.

```
clusterurl      http://activesn.bkp.ibm.com  
admincredentials    bWlk********3MHJk    
```   
* The clusterurl should be the vip of the cloudant local cluster.
* The admin credentials shoud be a base64encoding of the string `user:password` where the user is a cluster admin user.  

***for Elasticsearch target : Configuration data export - step1 (resources/export/elasticsearch/configuration/perfagent\_es_connection.info)***

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

***for Elasticsearch target : Configuration data export - step2 (resources/export/elasticsearch/configuration/certificates)***

Place your CAcert certificate at this location. You must match it with the filename identified in step1 above. 


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


***Configuration of Data Exclusions (resources/collect/configuration/perfagent\_stats\_exclusions.info)***

Proxy data is delineated by database that is accessed.

Some data can be excluded from collection to avoid distorting 'avg' statistics or for other reasons.

*Data from ***defined clientips*** can be excluded eg data from backup clusters.*

Use this file to define what you wish to ignore. See the configuration documentation for more details.

***Configuration of client Data Exclusions (resources/collect/configuration/clientdata\_stats\_exclusions.info)***

Client data is delineated by clientip that is interacting with the cluster.

Database stats per client are not available.

Per-client stats are useful in determining patterns of use by various REST clients.

Use this file to define what you wish to ignore. See the configuration documentation for more details.


***[Optional] Configuration of  Event Exclusions (perfagent\_events\_exclusions.info)***

Some data can be excluded from event-sensing to avoid unwanted repeated events or other reasons. 

Use this file to define what you wish to ignore. See the configuration documentation for more details.

***[Optional] Configuration of haproxy Event Thresholds (perfagent\_events\_thresholds.info)***

Use this file to define what you wish to signal as the limit for eventing. See the configuration documentation for more details.


***Executing Installation***

Once the configuration editing steps are done, go to `deploy` directory, and run `./clean_install.sh` 

Follow the prompts:  

* select mode(offline or not)
* target (es or pg) and whether to initialise schema or templates
  
This script will :  

* create a new installation in `/opt/cloudant-performancecollector` using the files contained in the `unpacking` area 
* backup any pre-existing `/opt/cloudant-performancecollector` content to a new directory `opt/cloudant-performancecollector-bkp-YYYYMMDDHHmm` where YYYYMMDDHHmm is the datetime of run of the install. You can delete this backup once you are happy with the running of the new installation
* create new service files in `/etc/init.d` and start them : services are created called `cpc_api_processor`
* backup any pre-existing service files in `/etc/init.d` for those services within `opt/cloudant-performancecollector-bkp-YYYYMMDDHHmm/init.d`. You can delete this backup once you are happy with the running of the new installation

The cpc_api_processor service in only needed for api based investigations.

#### Crontab configuration
Once the software is newly deployed, then the `root` user cron must be configured for periodic operation. It is recommended that :  
 
* proxydata\_every\_minute verb entry is enabled on each load-balancer (linked to local haproxy.log file)
* proxydata\_every\_minute endpoint entry is disabled on each load-balancer (linked to local haproxy.log file) and used only for investigative work
* clientdata\_every\_minute verb entry is enabled on each load-balancer (linked to local haproxy.log file)
* metricsdbdata\_every\_minute entry is enabled on just one load-balancer _(using the vip cluster address means it works even when it is not the primary)_
* volumedata\_every\_day is enabled on just one load-balancer _(using the vip cluster address means it works even when it is not the primary)_

Postgres target: The file `resources/export/postgres/templates/crontab.example` provides a template. Remember to only enable metrics and volumedb on ONE load balancer. Comment out or delete the lines one of the lbs.

ES target: The file `resources/export/elasticsearch/templates/crontab.example` provides a template. Remember to only enable metrics and volumedb on ONE load balancer. Comment out or delete the lines one of the lbs.

#### Configuring Grafana

***Configuring PostgreSQL datasource (for PostgreSQL export)***

For postgres export target, set up manually

```
a.	type = PostgreSQL
b.	host = postgreshost:5432
c.	database = postgres
d.	user = cloudant
e.	password = default is cloudant
f.	SSL mode = disable
g.	name = cloudantstats
```
Save & **test**.

***Configuring Elasticsearch datasources (for Elasticsearch export)***

For elasticsearch export target, 10 datasources are needed, and it is convenient to use the helper script  `datasources_install.sh` after you have installed the performancecollector.

This requires you to to be able to connect to Grafana from your load-balancer. This script also loads user and certificate data into the datasource, so saves a lot of time.

The script requires to login to grafana, so you need to set up connection details. It must be possible to access to curl to the grafana endpoint for the script to worl

* Configure grafana connection info 
(/opt/cloudant-performancecollector/resources/export/elasticsearch/grafana/grafana_connection.info)*

```
url		https://ldap.bkp.ibm.com:3000
credentials	YWRtaW46YWRtaW4K
```
* The url should be the url of the elasticsearch target. Include http/https and port.
* The access credentials shoud be a base64encoding of the string `user:password`   

https is supported, but certificate checking is not enabled.

You can generate the `credentials` string from the command prompt eg

```
[root@cl11c74lb1 configuration]# echo cloudant:passw0rd | base64
Y2xvdWRhbnQ6cGFzc3cwcmQK 
```   

* Run datasources installer
(/opt/cloudant-performancecollector/resources/export/elasticsearch/grafana/datasources_install.sh)*

Run this as `root`.

***Loading the dashboards***

Download the latest dashboards for your target from github to a pc or mac from `https://github.com/rombachuk/cloudant-performancedashboards`.   
Unpack the zip or pull individual <dashboard>.json files.

Then import the json files via grafana home page. Follow instructions on the cloudant-performancedashboards site for selection of datasources for imported dashbaords.


### Patch Install
This option is used when an upgrade to an existing installation is required. No changes to the configuration files are carried out, so cluster url and credentials, thresholds and exclusions are left as they are.  

The crontab for periodic jobs may need adjustment given the features changed or introduced in the patch. Release notes for the patch will indicate this.

Schema changes to postgres may be required. Release notes for the patch will indicate how to do this.

Do the installation as `root`

Go to `deploy` directory, and run `./patch_install.sh` 

This script will :  
  
* update the *.py files in `/opt/cloudant-performancecollector`
* update the *.sh files in `/opt/cloudant-performancecollector/perfagent_cronscript`
* backup any pre-existing `/opt/cloudant-performancecollector` content to a new directory `opt/cloudant-performancecollector-bkp-YYYYMMDDHHmm` where YYYYMMDDHHmm is the datetime of run of the install. You can delete this backup once you are happy with the running of the patched installation
* create new service files in `/etc/init.d` and start them : services are created called `cpc_api_processor`
* backup any pre-existing service files in `/etc/init.d` for those services within `opt/cloudant-performancecollector-bkp-YYYYMMDDHHmm/init.d`. You can delete this backup once you are happy with the running of the new installation





