#!/bin/bash 
# set -x
nowepoch=`date +%s`
let fromepoch=$nowepoch-$2*60
let toepoch=$nowepoch-$3*60
today=`date -d @$fromepoch +%Y%m%d`
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
/opt/cloudant-performancecollector/resources/collect/scripts/proxydata_minute_collect.sh $1 $frompretty $topretty $logfile
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
fi
rm -f $statsfile $eventsfile

