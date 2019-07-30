# Installing the performancecollector

### Planning your deployment

[architecture]: pc1.jpg

![architecture]
 
The overall architecture for performancecollector has :  

*	each load-balancer feeds haproxy log file with latest proxy data
*       each cluster provides volume data via \_all\_dbs endpoint of the cluster
*       cloudant-local clusters provide a metricsdb which consolidate per-minute stats data from each dbnode
*	processing of [proxy],[client],[body],[metricsdb] and [volume] data into metrics by the performancecollector
*       export of metrics to a target database (postgres or elasticsearch)
*	grafana-server and/or kibana-server and connects to postgres or elasticsearch datasource. 
*       user runs grafana dashboard on his browser which presents data from the datasource


The performancecollector is most conveniently installed on the one/two load balancers of a couchdb/cloudant-local cluster
The performancecollector is designed for use in RHEL7 or Centos7 hosted environments. 
 
This removes the overhead of forwarding latest proxy data to another server. This can be done if it is not possible to export directly to the database target from the load-balancer nodes.

The performancecollector causes bursts of high cpu usage on one core for about 10-20 seconds per minute if REST volumes are high, and this overhead must be accounted for in loadbalancer dimensioning.   

If dedicating a core on load-balancer servers to the performance collection is not acceptable, then :  

* the performancecollector should be installed on a distinct server
* haproxy.log files can be copied to these servers from load-balancers  


The performancecollector on each load-balancer exports its results to a database:  
*  Data is blank for the standby load-balancer. 
*  On a switchover, the new active load-balancer will process data and data rows will appear.
*  Volume & metricsdb data must be enabled on only one load-balancer. This type of collection should connect to the vip of the cluster to switch to the active load-balancer. If the load-balancer host fails entirely, then this data will not be available. The alternative is to run this collection from an independent node.

### Key Steps
Overall operation is summarised as :  

* performancecollector computes metrics from file and database sources and exports the results into a database.
* cloudant-performancedashboards content is used on **Grafana/Kibana**  to display the results from the  datasource.

The install requires several steps: 
  
* install and configuration of a target database (postgres or elasticsearch) on a server
* install and configuration of dashboarding-hub (grafana or kibana) on a server
* for postgres export target : install and configuration of postgres client on load-balancers
* configuration of haproxy to support http-log format for scraping by collector
* install and configuration of performancecollector on load-balancers, including the periodic collection schedule via cron



## Target Database

The target database must be operational prior to installation.

### PostgreSQL

For postgres, ensure that the 'root' user on the performancecollector host can access the PG instance via the psql client. Export is executed using psql commands from the linux shell. Ensure the connection details are configured in the resources/export/postgres/configuration directory during the installation. The instance can be initialised with the necessary schema during installation if the connection details are available.

### Elasticsearch

For elasticsearch, access is made using the python 'elasticsearch' driver. Ensure that the connection details are configured in the resources/export/elasticsearch/configuration directory during the installation. The instance can be initialised with the necessary templates for indexes during installation if the connection details are available.



## Dashboarding Hub

Grafana is preferable for this set of data. Kibana offers poorer hover-over data. Grafana can connect to elasticsearch perfectly well.

### Grafana

Install grafana on a server. The `cloudant-performancecollector` and `cloudant-performancedashboards` are designed to work with Grafana 5 or later.

Standard Grafana installation procedures can be used.

#### PostgreSQL database 

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

#### Elasticsearch database 
For elasticsearch export target, 10 datasources are needed, and it is convenient to use the helper script resources/export/elasticsearch/grafana/datasources_install.sh after you have installed the performancecollector.
This requires you to to be able to connect to Grafana from your load-balancer. This script also loads user and certificate data into the datasource, so saves a lot of time.

#### Loading the dashboards
Download the latest dashboards for your target from github to a pc or mac from `https://github.com/rombachuk/cloudant-performancedashboards`.   
Unpack the zip or pull individual <dashboard>.json files.

Then import the json files via grafana home page. Follow instructions on the cloudant-performancedashboards site for selection of datasources for imported dashbaords.


## Load Balancer haproxy configuration

####	Number of logline tokens (fields)
The /etc/haproxy/haproxy.cfg is used to define the log format of the haproxy.log file, and the number of fields.  

The standard haproxy configuration for Cloudant clusters does not include capture lines. This means the number of tokens per logfile line is 17.

If auditing is in place, then additional capture lines may appear. An example of capture lines for auditing is 
  
```
  capture request header Authorization len 256    
  capture cookie AuthSession= len 256  
```
The number of tokens is increased by the number of additional captures. So the haproxy.log will have 19 tokens in the above example. This number must be synchronised in a config file in the collector (see configuration).


## Performancecollector Install

### Postgres Target Only - Installation of Postgres Client

The standard postgres client for the operating system should be installed on each performancecollector server (load-balancer). There is no need to install postgresql-server.

For RHEL7 or Centos7, this can be achieved with 'yum install postgresql'

Once installed, test login to the postgres server is possible as linux user `root` using your postgres  pg-user an dpg-database using the `psql` tool :

  ```
  $ psql -U pg-user -d pg-database -h postgres-host
  psql> 
  ```  
  where postgres-host is the name of the postgres server. 


### Python libraries

The following library should be installed on each performancecollector server (load-balancer), as `root`   

`$ pip install pandas`

### Collecting software from Github

cloudant-performancecollector is released via github. Use a github client to download the release level required.

The github repository is 
`https://github.com/rombachuk/cloudant-performancecollector`

The releases option in Github shows the available releases.
Download from the site in either tar.gz or zip format, and place in a suitable directory, as `root` on the server eg `/root/software`


### 	Unpacking 
Then unpack the software with `tar xvf` or `unzip`, depending on the download format from github.

The software unpacks to the following directories :  
  
  * cloudant-performancecollector (the software to be installed)
  * documentation (markdown files documenting the package)
  * test (testing scripts for the package)
  * deploy (installation & patch scripts for the package)

#### Example

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
  
* configure haproxy token setup in `cloudant-performancecollector/resources/collect/configuration/perfagent_collect.conf`
* configure cluster access in `cloudant-performancecollector/resources/collect/configuration/perfagent_connection.info`
* postgres target: configure export target in `cloudant-performancecollector/resources/export/postgres/configuration` 
* es target: configure export target in `cloudant-performancecollector/resources/export/elasticsearch/configuration`
* configure exclusions for data collection (proxydata and clientdata)
* configure exclusions and thresholds for event-detection (proxydata only) - optional
* run the deploy/clean_install.sh script
* the installer will optionally build a new schema/template-set in the target :  
-- do this only on the first load-balancer install  
-- backup any old performance data you need
* configure crontab to run periodic metric collection jobs
* grafana hub: install datasources into grafana
* kibana hub: install index into kibana


Do the installation as `root`

#### Configuration (resources/collect/configuration/perfagent-collect.conf)
Align the base index in this file with the index number of the 'HTTP/1.1' field in the haproxy.log files (usually either 17 or 19). Index starts at 0. For example with no captures in the haproxy.log we would have :

`base_index	17`

#### Configuration (resources/collect/configuration/perfagent_connection.info)
Set up the access url and credentials for the cluster.

```
clusterurl      http://activesn.bkp.ibm.com  
admincredentials    bWlk********3MHJk    
```   
* The clusterurl should be the vip of the cloudant local cluster.
* The admin credentials shoud be a base64encoding of the string `user:password` where the user is a cluster admin user.  

#### Postgres target : Configuration (resources/export/postgres/configuration/perfagent\_pg_db.info)
Set up the hostname:db string for use by the postgres loading scripts.
The expected format is postgreshost:db . The :  is important

```
ldap.bkp.ibm.com:postgres    
```   
* The postgres host would be `ldap.bkp.ibm.com`.
* The postgres database would be `postgres` (postgres is the default).  


#### Postgres target : Configuration (resources/export/postgres/configuration/perfagent\_pg_credentials.info)
Set up the pguser:pgpassword as a base64 string for use by the postgres loading scripts. You can do this from the shell using 

```
$ echo cloudant:passw0rd | base64 > perfagent_pg_credentials.info    
```   
* The postgres user would be `cloudant`.
* The postgres password would be `passw0rd` 
* In the above example you would see the following contents in the file. 

`Y2xvdWRhbnQ6cGFzc3cwcmQK`


#### Configuration of proxy Data Exclusions (perfagent\_stats\_exclusions.info)

Proxy data is delineated by database that is accessed.

Some data can be excluded from collection to avoid distorting 'avg' statistics or for other reasons.

Data from defined clientips can be excluded eg data from backup clusters.

Use this file to define what you wish to ignore. See the configuration documentation for more details.

#### Configuration of client Data Exclusions (clientdata\_stats\_exclusions.info)

Client data is delineated by clientip that is interacting with the cluster.

Database stats per client are not available.

Per-client stats are useful in determining patterns of use by various REST clients.

Use this file to define what you wish to ignore. See the configuration documentation for more details.


#### Configuration of haproxy Event Exclusions (perfagent\_events\_exclusions.info)

Some data can be excluded from event-sensing to avoid unwanted repeated events or other reasons. 

Use this file to define what you wish to ignore. See the configuration documentation for more details.

#### Configuration of haproxy Event Thresholds (perfagent\_events\_thresholds.info)

Use this file to define what you wish to signal as the limit for eventing. See the configuration documentation for more details.


#### Installation

Once the configuration steps are done, go to `deploy` directory, and run `./clean_install.sh` 
  
This script will :  

* create a new installation in `/opt/cloudant-performancecollector` using the `conf` and `info` files contained in the installer's `cloudant-performancecollector` directory
* backup any pre-existing `/opt/cloudant-performancecollector` content to a new directory `opt/cloudant-performancecollector-bkp-YYYYMMDDHHmm` where YYYYMMDDHHmm is the datetime of run of the install. You can delete this backup once you are happy with the running of the new installation
* create new service files in `/etc/init.d` and start them : services are created called `cpc_api_processor`
* backup any pre-existing service files in `/etc/init.d` for those services within `opt/cloudant-performancecollector-bkp-YYYYMMDDHHmm/init.d`. You can delete this backup once you are happy with the running of the new installation

#### Crontab configuration
Once the software is newly deployed, then the `root` user cron must be configured for periodic operation. It is recommended that :  
 
* proxydata\_every\_minute verb entry is enabled on each load-balancer (linked to local haproxy.log file)
* proxydata\_every\_minute endpoint entry is disabled on each load-balancer (linked to local haproxy.log file) and used only for investigative work
* clientdata\_every\_minute verb entry is enabled on each load-balancer (linked to local haproxy.log file)
* metricsdbdata\_every\_minute entry is enabled on just one load-balancer _(using the vip cluster address means it works even when it is not the primary)_
* volumedata\_every\_day is enabled on just one load-balancer _(using the vip cluster address means it works even when it is not the primary)_

Postgres target: The file `resources/export/postgres/templates/crontab.example` provides a template. Remember to only enable metrics and volumedb on ONE load balancer. Comment out or delete the lines one of the lbs.

ES target: The file `resources/export/elasticsearch/templates/crontab.example` provides a template. Remember to only enable metrics and volumedb on ONE load balancer. Comment out or delete the lines one of the lbs.


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





