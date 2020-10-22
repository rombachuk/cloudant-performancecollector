#!/bin/bash 
# set -x
nowepoch=`date +%s`
let fromepoch=$nowepoch-$2*60
let toepoch=$nowepoch-$3*60
today=`date -d @$fromepoch +%Y%m%d`
frompretty=`date -d @$fromepoch +%Y%m%d%H%M`
topretty=`date -d @$toepoch +%Y%m%d%H%M`
fromgrep=`date -d @$fromepoch +%d/%b/%Y:%H:%M`
logfile=`echo "/opt/cloudant-performancecollector/tmp/"proxy$HOSTNAME"_"$1"_"$frompretty"_haproxy.log.gz"`
tail -n 500000 /var/log/haproxy.log | grep $fromgrep | gzip > $logfile
/opt/cloudant-performancecollector/resources/collect/scripts/proxydata_minute_collect.sh $1 $frompretty $topretty $logfile
rm -f $logfile
stats=`echo "stats_"$1"_by_minute_"$frompretty"_to_"$topretty`
findfile="find /opt/cloudant-performancecollector/results -name "$stats"* | tail -n 1"
statsfile=`eval $findfile`
events=`echo "events_"$1"_by_minute_"$frompretty"_to_"$topretty`
findfile="find /opt/cloudant-performancecollector/results -name "$events"* | tail -n 1"
eventsfile=`eval $findfile`
if [ $1 = "all" ]
then
allfile=`echo "/opt/cloudant-performancecollector/results/proxyall_"$today".csv"`
cat $statsfile | cut -d',' -f 4,5,17,19,22,38,42 | sed "1 d" >> $allfile
rm -f $statsfile $eventsfile
fi

