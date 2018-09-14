 
#	Overview
This works as described for api-based operation in 'link here', except : 
 
*	method  
-- the requests are made on the command line rather than an api call over REST  
*	results collection  
-- outputformat=json  
_results are stored in a cloudant database and must be collected via the \_api/perfagent via REST calls (see 'link')_  
-- outputformat=csv  
_results appear in the results directory specified in the perfagent.conf file (or via -R option), and can be viewed from there_  
* cron operation  
--	can be used to populate postgres ready for display in grafana (see 'link here')
* metrics supported  
--	additional compaction.py agent is available to gather various metrics useful for database & view size monitoring, and especially for compaction management _(these are not callable via the \_/api/perfagent endpoint at present)_   

#	Using the command line
The command line works exactly as the api, but instead of using a REST call with curl or code, you invoke the python script 

```
$ python perfagent.py [..options...]
```

The -O json option is not useful in this case. **Always use -O csv**, or set it as the default.  

All the defaults and options apply in the same way. See 'link here' for the details.

Logs go to /var/log/perfagent-collect.log and /var/log/csapi.log whether an api call or command line.
username and password are taken from perfagent_connection.info.

api call	command line equivalent
curl -u middleamd:*** "http://activesn.bkp.ibm.com/_api/perfagent" -X POST	/usr/bin/python /opt/cloudant-specialapi/perfagent.py 
curl -u middleamd:*** "http://activesn.bkp.ibm.com/_api/perfagent?outputformat=csv&fromtime=2018-01-16-22:00" -X POST	/usr/bin/python /opt/cloudant-specialapi/perfagent.py -O csv -f 2018-01-16-22:00
curl -u middleamd:*** "http://activesn.bkp.ibm.com/_api/perfagent?scope=database&granularity=day&from=201601150000&totime=now&outputformat=json&logfilehost=activesn.bkp.ibm.com" -X POST	/usr/bin/python /opt/cloudant-specialapi/perfagent.py -s database -g day -f 201601150000 -t now -O json -H activesn.bkp.ibm.com
not available via api call	/usr/bin/python /opt/cloudant-specialapi/compactionagent.py -x  /opt/cloudant-specialapi/perfagent_connection.info

#	Cron-based Collection to Postgres
 

The command line option can be used to setup regular minute-by-minute metrics collection, which is persisted to a _postgres_ database, for servicing the _grafana_ dashboards.

Grafana only postgres or mysql as SQL type sources out-of-the-box.  

This mode of operation uses cron scripts to run commands on a rolling timerange -> typically from 2 minutes to 1 minute from now.
The cron scripts run each minute.
##	Cron Operation Summary
It is convenient to set up a regular cronscript to capture data every minute, and display it on a dashboard.

Two scripts are provided :- 
 
* perfagent\_every\_minute.sh  
-- 	processes data in haproxy.log files  
* compactionagent\_every\_minute.sh  
-- reads data from cluster via REST 

### perfagent script (haproxy data)
The first script is used to populate one of ```[database_stats | verb_stats | endpoint_stats]``` tables in postgres, depending on the scope parameter ($1) used. It can be called several times to fill in the different scope levels, as required.

### compactionagent script (metrics db data)
The second script is used to populate the following performance data tables in postgres: 
 
* db\_stats  
* view\_stats  
* smoosh\_stats  
* ioq\_stats  
* host\_stats  

### example script
The provided example (/opt/cloudant-specialapi/perfagent\_cronscript/crontab\_example) can be used as a template to adjust to your particular setup.  It runs 'perfagent\_every\_minute' at both verb and endpoint scope levels. It runs compactionagent as well.  
##	HAproxy Collection (perfagent\_every\_minute.sh)  

### Overview  
A script, provided in directory /opt/cloudant-specialapi/crontab_example is given as an example. This is designed to be used with postgres as a target database, and grafana as a dashboard tool. But this can be adapted readily for other SQL-like datasources and reporting tools.

### Options  
The script uses the command line option and requires parameters for:-  

*	($1) scope of stats capture - one of [all | database | verb | endpoint | document]
*	($2) start-period for stats collection, set as (now - E) minutes
*	($3) end-period for stats collection, set as (now - S) minutes
*	($4) hostname for postgres server
*	($5) hostname of the log-provider (ie load-balancer) - use if loading from both lb-nodes.
*	($6) connection-info file (credentials) to cluster that is source of metrics

The start-period is typically 2, and the end-period is typically 1. This means the data is 1 minute old at time of collection.

### Characteristics
The script has the following characteristics:  

*	runs in crontab for root on the server where perfagent is installed.   
*	access to the haproxy logfile is required.   
-- 	If the perfagent is not on a Cloudant load-balancer, then rsyslog must be used to continually copy the haproxy.log file to the server that the perfagent runs on. Amend the following line in perfagent_minute.sh to point to your specific logfile name and location if it is different from below...

```
tail -n 500000 /var/log/haproxy.log | grep $fromgrep > $logfile
```

*	The script grabs 500000 last lines of the log file and matches the start-period minute. 
*	a command-line execution for perfagent using csv option is invoked on the resulting matches. 
*	writes the csv output content to the 'postgres' database as user 'cloudant' on hostname given by parameter $4 (can be changed by editing the perfagent\_every\_minute.sh file)
*	deletes temporary files and the results once it has loaded
*	takes about 2 seconds to execute where 15000 lines/minute are present

The script has been optimised to run as quickly as possible, so that the perfagent can run on both production load-balancers. However, load-balancer cpus can be freed if rsyslog is used to pipe the haproxy.log file to another server. See 'links here'

### Example
Set up crontab  :-  

```
[root@activesn perfagent_cronscript]# crontab -l
* * * * * /opt/cloudant-specialapi/perfagent_cronscript/perfagent_every_minute.sh verb 2 1 centos65-loader2.ibm.com activesn.bkp.ibm.com /opt/cloudant-specialapi/perfagent_connection.info > /dev/null 2>&1
* * * * * /opt/cloudant-specialapi/perfagent_cronscript/perfagent_every_minute.sh endpoint 2 1 centos65-loader2.ibm.com activesn.bkp.ibm.com /opt/cloudant-specialapi/perfagent_connection.info > /dev/null 2>&1
``` 

In this example  
 
*	it runs every minute, via root crontab, with errors not sent to email (remove the redirect to /dev/null to see errors in emails)
*	two runs are made - one at verb level, and one at the deeper endpoint level > so the 'verb_stats' and 'endpoint_stats' table is populated in postgres
*	the period that stats are captured for is 'now-2minutes to now-1minute'
*	the postgres server runs on centos65-loader2.ibm.com
*	the perfagent actually runs on the load-balancer host, and the logfilehost is activesn.bkp.ibm.com
*	the cluster is identified in the /opt/cloudant-specialapi/perfagent_connection.info file and this cluster-id is written on each row, so that the dashboards can be used with many clusters.

The log in /var/log/cloudant\_perfagent.log for a typical entry shows  

```
2018-01-29 19:00:02,792[execute_collect] (MainProcess) {cloudant performance agent} Request Processing for id [201801291900792585] time-boundary [201801291858-201801291859] Start
2018-01-29 19:00:02,795[find_dbstats] (MainProcess) {cloudant performance agent} Start of time boundary detected <201801291858> at line <1>
2018-01-29 19:00:02,799[execute_collect] (MainProcess) {cloudant performance agent} Request Processing for id [201801291900792585] Log Lines Found = [36]
2018-01-29 19:00:02,930[execute_collect] (MainProcess) {cloudant performance agent} Request Processing for id [201801291900792585] Resource Groups Found = [4]
2018-01-29 19:00:02,933[generate_stats_output] (MainProcess) {cloudant performance agent} Request Processing for id [201801291900792585] Stats Lines Generated = [4]
2018-01-29 19:00:02,940[generate_events_output] (MainProcess) {cloudant performance agent} Request Processing for id [201801291900792585] Event Lines Generated = [0]
2018-01-29 19:00:02,940[execute_collect] (MainProcess) {cloudant performance agent} Request Processing for id [201801291900792585] End
```  
## compactionagent script (metrics-db derived data)
### Overview
A script, provided in directory /opt/cloudant-specialapi/crontab_example is given as an example. This is designed to be used with postgres as a target database, and grafana as a dashboard tool. But this can be adapted readily for other SQL-like datasources and reporting tools.

### Options
The script uses the command line option and requires parameters for:-  

*	($1) hostname for postgres server
*	($2) connection-info file (credentials) to cluster that is source of metrics

### Characteristics
The script has the following characteristics:  

*	runs in crontab for root on the server where perfagent is installed. 
*	accesses the cluster via python REST calls to gather data useful for compaction monitoring
*	accesses the cluster via python REST calls to gather some data from the metrics database which must be active and populated each minute 
*	generates csv output for each of the statistics levels collected (db,view,ioq,smoosh,host). 
*	writes the csv output content to the 'postgres' database as user 'cloudant' on hostname given by parameter $1 (can be changed by editing the perfagent\_every\_minute.sh file)
*	deletes temporary files and the results once it has loaded

This script is designed to collect the 'latest' information from the cluster, and be run every minute. The metrics database has a 1 minute lag in timestamping its data. This can lead to lags between compaction and perfagent (haproxy) timestamps, and data point gaps in grafana dashboards.

Example
[root@activesn perfagent_cronscript]# crontab -l
* * * * * /opt/cloudant-specialapi/perfagent_cronscript/compactionagent_every_minute.sh centos65-loader2.ibm.com /opt/cloudant-specialapi/perfagent_connection.info > /dev/null 2>&1

In this example 
•	it runs every minute, via root crontab, with errors not sent to email (remove the redirect to /dev/null to see errors in emails)
•	one run is needed which collects all the necessary stats
•	the period is always just the last minute
•	the postgres server runs on centos65-loader2.ibm.com
•	in this case the compactionnagent actually runs on the load-balancer host. If you have 2 load-balancers, run this script on only one of them.  
##	Installation for Periodic Operation
###	Architecture

[architecture]: perfagent-architecture.png

![architecture]
 
The preferred architecture has :  

*	each load-balancer (A,B) forwarding its respective haproxy.log file to an input directory on the perfagent client server (C)
*	scripts for each load-balancer scan the input haproxy.log file, and pump statistics for period now-2minutes to now-1minute to a postgres server D. postgres client is installed on C. Files are made on server C and loaded to server D using the postgres '\copy' command.
*	scripts for compaction scan the cluster and generate csv for copy to server D. These scripts can be 
*	postgres server D supports tables for haproxy-log stats and the compaction stats 
*	postgres server must open port 5432 &/or 5432 to C and E
*	grafana runs on server E and connects to datasource on D. dashboard for grafana available which is fitted to the data coming from C.
*	grafana server must open port 3000 to users
*	other scripts will be made available and will be released with a corresponding dashboard  

It is possible to combine the roles shown above :  
 
*	perfagent can run on each load-balancer, but requires bursts of cpu capacity  -> approximately 2 seconds of a cpu per 15k haproxy lines/sec
*	postgres server could run on grafana server E

###	postgres server
Ensure port 5432 is not blocked by firewall.
Install postgresql-server and postgresql (client). The procedure varies per OS and postgres version.
For RHEL7.4, and postgres942, do this as root:  

1)	`$ yum -y install `  
`https://download.postgresql.org/pub/repos/yum/9.4/redhat/rhel-7-x86_64/pgdg-redhat94-9.4-2.noarch.rpm`
2)	`$ yum -y install postgresql94`  
3)	`$ yum -y install postgresql94-server`  
4)	`$ /usr/pgsql-9.4/bin/postgresql94-setup initdb`  
5)	`$ systemctl enable postgresql-9.4`  
6)	`$ systemctl start postgresql-9.4`   
7) switch user to postgres, using `$ su - postgres`  
8)	modify the default security to passwords, using  
	a) `psql -U postgres`  
	b) within the psql shell  
		i) `alter user postgres password 'postgres';`  
   		ii) `create user cloudant with superuser password 'cloudant';`  
   		iii) exit psql with `\q`  
   	c) edit the file /var/lib/pgsql/9.4/data/pg_hba.conf, and modify as :
   	
``` 
# "local" is for Unix domain socket connections only
local   all             all                                     password
# IPv4 local connections:
host    all             all             127.0.0.1/32            password
host    all             all             192.168.254.184/24       password
host    all             all             192.168.254.61/24       password
# IPv6 local connections:
host    all             all             ::1/128                 password
```  

Ensure the methods are `password` as above.  
Ensure that IPv4 local client host lines exist for all clients.  

In the example above, the perfagent-client is 192.168.254.61 and the grafana-server is 192.168.254.184. You can use hostnames if you like. Without these lines, you cannot login to postgres from those boxes.


   d) edit the file /var/lib/pgsql/9.4/data/postgresql.conf, and modify as :
   
```
listen_addresses = 'localhost,postgres-host.fqdn'
```

Ensure the listen_addresses has the hostname of the postgres server in the list.
Without this, access to postgres is limited to localhost (ie 127.0.0.1)

   e) restart postgres as root, using `systemctl restart postgres-9.4`  
   f) test that root can now logon to postgres, using  
   `$ psql -U cloudant -d postgres -h postgres-host`
       with password `cloudant` or what you have set

If this is ok. then the perfagent can be configured to connect to _postgres_, and log statistics for grafana to _display_.

###	perfagent client
It is assumed that the perfagent itself is installed on the perfagent client server.  

To install the perfagent software itself see [Installing the specialapi](./Installation.md#installing-the-specialapi).  

The additional step,after the perfagent is installed is to:
•	install postgres client
For RHEL7.4, do this as root:  

1)	`$ yum -y install`  
`https://download.postgresql.org/pub/repos/yum/9.4/redhat/rhel-7-x86_64/pgdg-redhat94-9.4-2.noarch.rpm`
2)	`$ yum -y install postgresql94`

Now test that you can logon to postgres, using
	`$ psql -U cloudant -d postgres -h postgres-host`
       with password 'cloudant' or what you have set

If ok, exit psql with `\q` and run the two schemas script with: 
 
`$ psql -U cloudant -d postgres -h postgres-host -f /opt/cloudant-specialapi/perfagent_postgres.sql`
and
`$ psql -U cloudant -d postgres -h postgres-host -f /opt/cloudant-specialapi/compactionagent_postgres.sql`

with password 'cloudant'

Note that you can clean out data from any previous versions of the perfagent using 
`$ psql -U cloudant -d postgres -h postgres-host -f /opt/cloudant-specialapi/perfagent_postgres_drop.sql`
and 
`$ psql -U cloudant -d postgres -h postgres-host -f /opt/cloudant-specialapi/compactionagent_postgres_drop.sql`


If ok, then setup the per\_minute cronjobs using the example in `/opt/cloudant-specialapi/crontab_example` see also [cron setup](#cron-based-collection-to-postgres) 

1)	modify centos65-loader2.ibm.com to be your postgres-server hostname  
2)	modify activesn.bkp.ibm.com to be your load-balancer logfile source  
3)	add the line to root's crontab  
4)	add a line for each load-balancer source if one server is collecting for two load-balancers.  

Test the script by inspecting the table `verb_stats` using psql as above:  
```
select * from verb_stats where mtime = (select max(mtime) from verb_stats);
```

The logfile `/var/log/cloudant_perfagent.log` provides run-by-run logging of the cronjob.   

You can also debug by looking at the mail output of the cronjob, and also by commenting out the `set -x` line in `/opt/cloudant-specialapi/perfagent_cronscript/perfagent_every_minute.sh`

### grafana server
Grafana is installed via yum on its server. Grafana is frequently updated. The instructions below are an example and apply to grafana-4.6.3-1 only.

For RHEL7.4, do this as root:
1)	`$ yum -y install https://download.postgresql.org/pub/repos/yum/9.4/redhat/rhel-7-x86_64/pgdg-redhat94-9.4-2.noarch.rpm`
2)	`$ yum -y install postgresql94`
3)	`yum -y install https://s3-us-west-2.amazonaws.com/grafana-releases/release/grafana-4.6.3-1.x86_64.rpm`
4)	`systemctl enable grafana-server`
5)	`systemctl restart grafana-server`

Grafana is configured via the web on port 3000.  
Access grafana with account 'admin/admin'. Change credentials as you wish.

1)	Set up a datasource: 

```
a)	type = PostgreSQL  
b)	host = postgreshost:5432  
c)	database = postgres  
d)	user = cloudant  
e)	password = cloudant  
f)	SSL mode = disable  
g)	name = cloudantstats 
```   
   
2)	Populate dashboards using a browser:  

```
a) from /opt/cloudant-specialapi/grafana_dashboards copy the dashboards to your desktop client pc or mac. 
b) Then import via grafana home page. Choose cloudantstats as your datasource.
```

3)	Adjust the templating to fit your project naming and sharding:  

a) The dashboards use templating to delineate projects (using _ as the project boundary marker), and also to set node numbers per cluster. Change this logic in the Settings->Templating to suit your particular cluster names and node numbers and sharding setup.

_default SQL for project variable_ 
 
```
SELECT CASE WHEN substring(database,0,position('_' in database)) = ''   
THEN 'others' ELSE substring(database,0,position('_' in database)) END as project  
from db_stats where cluster=$cluster and database is not null   
group by project order by project
```			

_default SQL for num\_nodes_  

```
SELECT case when cluster like '%activesn.bkp.ibm.com' then 1  
 when cluster like '%cl11c74vip.ibm.com' then 3 else 3 end   
 from smoosh_stats where cluster=$cluster
```  
_default SQL for shards\_per\_node variable_

```
SELECT case when cluster like '%activesn.bkp.ibm.com' then 8  
when cluster like '%cl11c74vip.ibm.com' then 8 else 8 end   
from smoosh_stats where cluster=$cluster
```  

4)	Inspect tha plots refresh each minute  
 
* If postgres is receiving stats from perfagent, and the compactionagent, you should see plots immediately, they refresh each minute.  

5)	Adjust plot using standard grafana features to select individual dbs and other parameters.  

6)	The panel can be modified by   

* selecting the title and clicking edit.
* One very useful option is to go to 'Display' and change Hover Tooltip-> StackedValue to cumulative. This shows a total in the hover. You can switch it back to individual as suits.

#### Example dashboard

[dashboard]: dashboard.png
![dashboard]
 
