 
#	Overview
This feature allows more detailed/granular metrics to be collected for short periods. 

This can mean :

* increasing the resource levels of metrics from per-database to per-database-endpoint (proxydata or clientdata)
* increasing the collection rate from per-day to per-hour or per-minute (volumedata)

Dashboards are available to support these types of investigation.
 
The performancecollector supports a powerful set of options to process investigative collections of haproxy data at various resource levels (scope) and time-rollups (granularity).   

The user can build shell scripts with these options and feed postgres and grafana. Custom schema creation and dashboard building may be required. In these cases, consultancy from IBM is recommended. 

## Endpoint Level Investigations

This enables collection of proxy-sourced data for every database-endpoint combination occurring on the cluster. 

This can be very useful in tracking :

* POST to \_find or \_design (which can be reads)
* determining documentlevel volumes
* many other things
 
This will likely lead to 10-20 times the row count per minute, so should be limited to short time periods.

It can be enabled simply by removing the commented line in root's `crontab` relating to `proxydata_every_minute endpoint` -> note the postgres host and lb host should be the same as for `proxydata_every_minute verb` entry.

The table `endpoint_stats` should be loaded from each per-minute run.

Disable once investigationa are complete.

## Body Level Investigations

This enables collection of proxy-sourced data for every database-endpoint-body combination occurring on the cluster. Body content must be enabled in the haproxy to make use of this option. Consult the author for assistance with this.

This can be very useful in tracking :

* very detailed query analysis 
 
This will likely lead to many times the row count per minute, or per second, so should be limited to short time periods.

You should run the following schema script to set up tables. Volumes can be high so be careful to clean these tables up after a run :-

`bodydata_postgres.sql`

###Per Minute Granularity

It can be invoked at minute granularity using the minute_onetime script. See the following example :

```
 /opt/cloudant-performancecollector/perfagent_cronscript/bodydata_minute_onetime.sh  
  201901291134 201901291139 primary.ibm.com /var/log/haproxy.log
```

In the example above, detailed body stats per minute are gathered for   

* starttime `2019-01-29 11:34`
* endtime `2019-01-29 11:39`
* haproxy-hosttag   `primary.ibm.com`
* logfile scanned in `/var/log/haproxy.log`

The table `body_endpoint_stats` should be loaded from each per-minute run.
postgres and cluster credentials are set up in the same way as the cronjobs.

This script is a feeder to the Traffic Detail performance dashboards.

Disable once investigations are complete.

###Per Second Granularity

It can be invoked at second granularity using the minute_onetime script. See the following example :

```
 /opt/cloudant-performancecollector/perfagent_cronscript/bodydata_second_onetime.sh  
  201901291134 201901291135 primary.ibm.com /var/log/haproxy.log
```

In the example above, detailed body stats per second are gathered for   

* starttime `2019-01-29 11:34`
* endtime `2019-01-29 11:35`
* haproxy-hosttag   `primary.ibm.com`
* logfile scanned in `/var/log/haproxy.log`

The table `body_endpoint_stats_s` should be loaded from each per-minute run.
postgres and cluster credentials are set up in the same way as the cronjobs. 
Keep the time range short.

This script is a feeder to the Traffic Detail performance dashboards.

Disable once investigations are complete.


## Per-hour or Per-minute Volume Data Investigations

This allows compaction issues and fast growing databases to be tracked at finer time granularity than once a day.

It can be enabled by simply using cron to change the interval of the `volumedata_every_day` script, which can be run at a finer level in fact.

To run every hour at 30 minutes past the hour, change `30 11` to `30 *`  
To run every minute , change `30 11` to `* *`

This script makes traffic on the cluster using REST calls : `2 GETs per db and 2 GETs per view`   

It should be enabled only for limited periods when db and view numbers are high.

## Special Investigations
The scripts can be used to scan proxy files over periods wider than 1 minute and can collect a lot of data via these methods.

You can configure cron to run collections at known problem times for later review.

See **Proxydata Collection Options** for more details of the perfagent command line syntax (same as the api job options).
