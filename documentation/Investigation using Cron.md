 
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
