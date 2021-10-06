#!/bin/bash 
# set -x
nowepoch=`date +%s`
let fromepoch=$nowepoch-$2*60
let toepoch=$nowepoch-$3*60
today=`date -d @$fromepoch +%Y%m%d`
frompretty=`date -d @$fromepoch +%Y%m%d%H%M`
topretty=`date -d @$toepoch +%Y%m%d%H%M`
fromgrep=`date -d @$fromepoch +%d/%b/%Y:%H:%M`
logfile=`echo "/opt/cloudant-performancecollector/tmp/"client$HOSTNAME"_"$1"_"$frompretty"_haproxy.log.gz"`
tail -n 500000 /var/log/haproxy.log | grep $fromgrep | gzip > $logfile
/opt/cloudant-performancecollector/resources/collect/scripts/clientdata_minute_collect.sh $1 $frompretty $topretty $logfile
rm -f $logfile
stats=`echo "clientstats_"$1"_by_minute_"$frompretty"_to_"$topretty`
findfile="find /opt/cloudant-performancecollector/results -name "$stats"* | tail -n 1"
statsfile=`eval $findfile`
events=`echo "clientevents_"$1"_by_minute_"$frompretty"_to_"$topretty`
findfile="find /opt/cloudant-performancecollector/results -name "$events"* | tail -n 1"
eventsfile=`eval $findfile`
if [ $1 = "client" ]
then
bysourcefile=`echo "/opt/cloudant-performancecollector/results/bysource_"$today".csv"`
if [  ! -f $bysourcefile ]; then
echo "sourceip,timestamp,epoch,database_response_time_avg,cloudant_requests,e2e_response_time_avg" > $bysourcefile
fi
cat $statsfile | cut -d',' -f 4,5,6,18,20,23 | sed "1 d" >> $bysourcefile
fi
rm -f $statsfile $eventsfile