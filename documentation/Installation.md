# Installing the performancecollector

### Planning your deployment

[architecture]: perfagent-architecture.png

![architecture]
 
The overall architecture for performancecollector has :  

*	each load-balancer (A,B) forwards latest proxy data to the  performancecollector (C)
*	processing of [proxy],[metricsdb] and [cluster volume] data into metrics by the performancecollector
*   metrics are checked against thresholds to generate `events` files which can be used by an event-tool `eg IBM Netcool` to signal failure modes to admin operators
*	periodic (per-minute or daily for cluster-volumes) delivery of metrics into postgres database (D) from the performancecollector
*	grafana server (E) and connects to postgres datasource. 
*  user runs grafana dashboard on his browser which presents data from the datasource
*  _optional ad-hoc collection runs via special api, with results delivered in json-format within a cloudant document (see api-based collection section)_

The performancecollector is most conveniently installed on the two load balancers of a cloudant local cluster: ie function C above is located on servers A and B.

The performancecollector is designed for use in RHEL7 or Centos7 hosted cloudant cluster environments. 
 
This removes the overhead of forwarding latest proxy data to another server, and the effort of maintaining another server for function C.

The performancecollector causes bursts of high cpu usage on one core for about 10-20 seconds per minute if REST volumes are high, and this overhead must be accounted for in loadbalancer dimensioning.   

If dedicating a core on load-balancer servers to the performance collection is not acceptable, then :  

* the performancecollector should be installed on a distinct server
* haproxy.log files can be copied to these servers from load-balancers  
* contact the cloudant-performancecollector support team for specific assistance


The performancecollector on each load-balancer sends its results to a postgres database:  
  
*  Data is blank for the standby load-balancer. 
*  On a switchover, the new active load-balancer will process data and data rows will appear.

The postgres database should be on a separate server to the load-balancers. It may be convenient to combine functions D and E (ie co-locate postgres database and grafana server functions on one host).




### Key Steps
Overall operation is summarised as :  

* performancecollector computes metrics from file and database sources and loads the results into a **postgres** database
* cloudant-performancedashboards content is used on **Grafana**  to display the results from the postgres datasource.

The install requires several steps: 
  
* install and configuration of postgres database on a server
* install and configuration of grafana on a server
* install and configuration of postgres client on load-balancers
* configuration of haproxy to support collection on load-balancers
* install and configuration of performancecollector on load-balancers, including the periodic collection schedule via cron
* _optional set up of ad-hoc api-based collection jobs_


## Postgres Server Install

Postgres server can be installed on any server, or an existing postgres server can be used. Postgres by default does not use the account/password type login method. 

For RHEL or Centos, `yum install postgresql-server` will install 8.4 but more recent releases can be installed by using the explicit version number eg `yum install postgresql94-server`  

Once the service is running, it must be configured to allow the performancecollector and grafana to connect using account names and passwords:

* as user `postgres`, modify the default security check to passwords, using the following steps :  
  -- adjust the accounts so they have passwords via `psql` shell  
  
  ```  
  $ psql -U postgres
  psql> alter user postgres password 'postgres';
  psql> create user cloudant with superuser password 'cloudant';
  psql>\q
  ```  
  
  -- edit the file pg_hba.conf file (usually located in `/var/lib/pgsql/9.4/data/)`, and modify as :  
  
  
  ```       
  # "local" is for Unix domain socket connections only
  local   all             all                                     password
  # IPv4 local connections:
  host    all             all             127.0.0.1/32            password
  host    all             all             192.168.254.184/24      password
  host    all             all             192.168.254.61/24       password
  # IPv6 local connections:
  host    all             all             ::1/128                 password
  ```  
  
  ensure the methods are 'password' as above.  
  ensure that IPv4 local client host lines exist for all clients.   
_In the example above, the performancecollector is 192.168.254.61 and the grafana-server is 192.168.254.184. You can use hostnames if you like. Without these lines, you cannot login to postgres from those boxes._

  -- edit the file postgresql.conf (usually located in `/var/lib/pgsql/9.4/data/)`, and modify as:
  
  ```
  listen_addresses = 'localhost,postgres-host.fqdn'
  ```  

  ensure the listen_addresses has the hostname of the postgres server in the list.
Without this, access to postgres is limited to localhost (ie 127.0.0.1)

* restart postgres as `root`, using `systemctl restart postgres-9.4`  
* test that `root` linux user can now logon to postgres, using
	`$ psql -U cloudant -d postgres -h postgres-host`
       with password 'cloudant'

If this is ok. then the perfagent can be configured to connect to postgres, 

## Grafana Server Install

Install grafana on a server. The `cloudant-performancecollector` and `cloudant-performancedashboards` are designed to work with Grafana 5 or later.

Standard Grafana installation procedures can be used.

Grafana is usually configured via the web on port 3000.
Access grafana with account `admin` and the password. 

Set up a datasource using the Grafana web interface :  

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


Download the latest dashboards from github to a pc or mac from `https://github.com/rombachuk/cloudant-performancedashboards`.   
Unpack the zip or pull individual <dashboard>.json files.

Then import the json files via grafana home page. Choose `cloudantstats` as your datasource.


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

### Postgres Client

The standard postgres client for the operating system should be installed on each performancecollector server (load-balancer). There is no need to install postgresql-server.

For RHEL7 or Centos7, this can be achieved with 'yum install postgresql'

Once installed, test login to the postgres server is possible as linux user `root` using postgres user `cloudant` using the `psql` tool :

  ```
  $ psql -U cloudant -d postgres -h postgres-host
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
  
* configure haproxy token setup in `cloudant-performancecollector/perfagent_collect.conf`
* configure cluster access for metricsdb based stats in `cloudant-performancecollector/perfagent_connection.info`
* configure exclusions for data collection
* configure exclusions and thresholds for event-detection
* run the deploy/clean_install.sh script
* the installer will optionally build a new schema in postgres :  
-- do this only on the first load-balancer install  
-- backup any old performance data you need
* configure crontab to run periodic metric collection jobs


Do the installation as `root`

#### Configuration (perfagent-collect.conf)
Align the base index in this file with the Number of logline tokens (fields) set up in the haproxy.log files (usually either 17 or 19), for example with no captures in the haproxy.log we would have :

`base_index	17`

#### Configuration (perfagent_connection.info)
Set up the access url and credentials for the cluster.

```
clusterurl      http://activesn.bkp.ibm.com  
admincredentials    bWlk********3MHJk    
```   
* The clusterurl should be the vip of the cloudant local cluster.
* The admin credentials shoud be a base64encoding of the string `user:password` where the user is a cluster admin user.  

#### Configuration of haproxy Data Exclusions (perfagent\_stats\_exclusions.info)

Some data can be excluded from collection to avoid distorting 'avg' statistics or for other reasons.

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
 
* proxydata\_every\_minute entry is enabled on each load-balancer (linked to local haproxy.log file)
* metricsdbdata\_every\_minute entry is enabled on just one load-balancer _(using the vip cluster address means it works even when it is not the primary)_
* volumedata\_every\_day is enabled on just one load-balancer _(using the vip cluster address means it works even when it is not the primary)_

The file `perfagent_results/crontab.example` provides a template. Consult the Configuration document for this tool to set the parameters to those appropriate for your cluster.


### Patch Install
This option is used when an upgrade to an existing installation is required. No changes to the configuration files are carried out, so cluster url and credentials, thresholds and exclusions are left as they are.  

The crontab for periodic jobs may need adjustment given the features changed or introduced in the patch. Release notes for the patch will indicate this.

Schema changes to postgres may be required. Release notes for the patch will indicate how to do this.

Do the installation as `root`

Go to `deploy` directory, and run `./patch_install.sh` 

This script will :  
  
* update the *.py files in `/opt/cloudant-performancecollector`
* backup any pre-existing `/opt/cloudant-performancecollector` content to a new directory `opt/cloudant-performancecollector-bkp-YYYYMMDDHHmm` where YYYYMMDDHHmm is the datetime of run of the install. You can delete this backup once you are happy with the running of the patched installation
* create new service files in `/etc/init.d` and start them : services are created called `cpc_api_processor`
* backup any pre-existing service files in `/etc/init.d` for those services within `opt/cloudant-performancecollector-bkp-YYYYMMDDHHmm/init.d`. You can delete this backup once you are happy with the running of the new installation





