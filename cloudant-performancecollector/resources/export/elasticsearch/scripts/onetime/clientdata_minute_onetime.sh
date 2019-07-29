#!/bin/bash
# set -x
source /opt/cloudant-performancecollector/venv/bin/activate
/opt/cloudant-performancecollector/resources/collect/scripts/clientdata_minute_collect.sh $1 $2 $3 $4 
/opt/cloudant-performancecollector/venv/bin/python /opt/cloudant-performancecollector/es_exporter.py -d client -g minute -s $1 -f $2 -t $3
stats=`echo "clientstats_"$1"_by_minute_"$frompretty"_to_"$topretty`
findfile="find /opt/cloudant-performancecollector/results -name "$stats"* | tail -n 1"
statsfile=`eval $findfile`
events=`echo "clientevents_"$1"_by_minute_"$frompretty"_to_"$topretty`
findfile="find /opt/cloudant-performancecollector/results -name "$events"* | tail -n 1"
eventsfile=`eval $findfile`
rm -f $statsfile $eventsfile
