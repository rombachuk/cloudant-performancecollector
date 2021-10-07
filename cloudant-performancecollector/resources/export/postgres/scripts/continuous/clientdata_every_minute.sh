#!/bin/bash 
# set -x
nowepoch=`date +%s`
let fromepoch=$nowepoch-$2*60
let toepoch=$nowepoch-$3*60
frompretty=`date -d @$fromepoch +%Y%m%d%H%M`
topretty=`date -d @$toepoch +%Y%m%d%H%M`
fromgrep=`date -d @$fromepoch +%d/%b/%Y:%H:%M`
logfile=`echo "/opt/cloudant-performancecollector/tmp/"finaltail$HOSTNAME"_"$frompretty"_haproxy.log.gz"`
counter=0
until [[ -f $logfile ]] || [[ $counter -gt 60 ]]
 do
 sleep 1
 ((counter++))
 done
/opt/cloudant-performancecollector/resources/collect/scripts/clientdata_minute_collect.sh $1 $frompretty $topretty $logfile
/opt/cloudant-performancecollector/resources/export/postgres/scripts/onetime/clientdata_minute_load.sh $1 $frompretty $topretty
stats=`echo "clientstats_"$1"_by_minute_"$frompretty"_to_"$topretty`
findfile="find /opt/cloudant-performancecollector/results -name "$stats"* | tail -n 1"
statsfile=`eval $findfile`
events=`echo "clientevents_"$1"_by_minute_"$frompretty"_to_"$topretty`
findfile="find /opt/cloudant-performancecollector/results -name "$events"* | tail -n 1"
eventsfile=`eval $findfile`
rm -f $statsfile $eventsfile
