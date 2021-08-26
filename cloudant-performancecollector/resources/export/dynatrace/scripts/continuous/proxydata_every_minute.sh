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
netstatoldfile=`echo "/opt/cloudant-performancecollector/tmp/netstatold"`
if [  ! -f $allfile ]; then
echo "timestamp,epoch,database_response_time_avg,cloudant_requests,e2e_response_time_avg,fe_connections,be_connections,udp_packet_loss" > $allfile
fi
cloudant_stats=`cat $statsfile | cut -d',' -f 4,5,17,19,22,38,42 | sed "1 d"`
current_udp_packet_receive_errors=`netstat -suna | grep 'packet receive errors' | tr -s ' ' | cut -d' ' -f 2`
if [ ! -f $netstatoldfile ]; then
echo $current_udp_packet_receive_errors > $netstatoldfile
echo $cloudant_stats",0" >> $allfile
else
previous_udp_packet_receive_errors=`cat $netstatoldfile`
let udp_packet_receive_errors=$current_udp_packet_receive_errors-$previous_udp_packet_receive_errors
echo $current_udp_packet_receive_errors > $netstatoldfile
echo $cloudant_stats","$udp_packet_receive_errors >> $allfile
fi
dynatracefile=`echo "/opt/cloudant-performancecollector/results/dynatrace.sh"`
epoch=`cat $statsfile | cut -d',' -f 5 | sed "1 d"`
cloudantdatabaseresponsetimeavg=`cat $statsfile | cut -d',' -f 17 | sed "1 d"`
cloudantrequests=`cat $statsfile | cut -d',' -f 19 | sed "1 d"`
cloudante2eresponsetimeavg=`cat $statsfile | cut -d',' -f 22 | sed "1 d"`
haproxyfeconnections=`cat $statsfile | cut -d',' -f 38 | sed "1 d"`
haproxybeconnections=`cat $statsfile | cut -d',' -f 42 | sed "1 d"`
echo "dynatrace_ingest 'cloudant.database_response_time' '$cloudantdatabaseresponsetimeavg' '$epoch""000'" > $dynatracefile
echo "dynatrace_ingest 'cloudant.requests' '$cloudantrequests' '$epoch""000'" >> $dynatracefile
echo "dynatrace_ingest 'cloudant.e2e_response_time' '$cloudante2eresponsetimeavg' '$epoch""000'" >> $dynatracefile
echo "dynatrace_ingest 'haproxy.frontend_connections' '$haproxyfeconnections' '$epoch""000'" >> $dynatracefile
echo "dynatrace_ingest 'haproxy.backend_connections' '$haproxybeconnections' '$epoch""000'" >> $dynatracefile
echo "dynatrace_ingest 'haproxy.udp_packet_loss' '$udp_packet_receive_errors' '$epoch""000'" >> $dynatracefile
fi
rm -f $statsfile $eventsfile

