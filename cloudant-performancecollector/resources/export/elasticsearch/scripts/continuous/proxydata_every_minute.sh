#!/bin/bash 
 set -x
nowepoch=`date +%s`
let fromepoch=$nowepoch-$2*60
let toepoch=$nowepoch-$3*60
frompretty=`date -d @$fromepoch +%Y%m%d%H%M`
topretty=`date -d @$toepoch +%Y%m%d%H%M`
fromgrep=`date -d @$fromepoch +%d/%b/%Y:%H:%M`
logfile=`echo "/opt/cloudant-performancecollector/tmp/"proxy$HOSTNAME"_"$1"_"$frompretty"_haproxy.log.gz"`
tail -n 500000 /var/log/haproxy.log | grep $fromgrep | gzip > $logfile
/opt/cloudant-performancecollector/resources/collect/scripts/proxydata_minute_collect.sh $1 $frompretty $topretty $logfile
/usr/bin/python /opt/cloudant-performancecollector/es_exporter.py -d proxy -g minute -s $1 -f $frompretty -t $topretty
rm -f $logfile
stats=`echo "stats_"$1"_by_minute_"$frompretty"_to_"$topretty`
findfile="find /opt/cloudant-performancecollector/results -name "$stats"* | tail -n 1"
statsfile=`eval $findfile`
events=`echo "events_"$1"_by_minute_"$frompretty"_to_"$topretty`
findfile="find /opt/cloudant-performancecollector/results -name "$events"* | tail -n 1"
eventsfile=`eval $findfile`
rm -f $statsfile $eventsfile
