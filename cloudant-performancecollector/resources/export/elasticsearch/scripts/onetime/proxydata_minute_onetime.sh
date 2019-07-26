#!/bin/bash
# set -x
/opt/cloudant-performancecollector/resources/collect/scripts/proxydata_minute_collect.sh $1 $2 $3 $4 
/usr/bin/python /opt/cloudant-performancecollector/es_exporter.py -d proxy -g minute -s $1 -f $2 -t $3
stats=`echo "stats_"$1"_by_minute_"$frompretty"_to_"$topretty`
findfile="find /opt/cloudant-performancecollector/results -name "$stats"* | tail -n 1"
statsfile=`eval $findfile`
events=`echo "events_"$1"_by_minute_"$frompretty"_to_"$topretty`
findfile="find /opt/cloudant-performancecollector/results -name "$events"* | tail -n 1"
eventsfile=`eval $findfile`
rm -f $statsfile $eventsfile
