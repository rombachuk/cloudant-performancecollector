##!/bin/bash 
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
/opt/cloudant-performancecollector/resources/collect/scripts/clientdata_minute_collect.sh $1 $frompretty $topretty $logfile
stats=`echo "clientstats_"$1"_by_minute_"$frompretty"_to_"$topretty`
findfile="find /opt/cloudant-performancecollector/results -name "$stats"* | tail -n 1"
statsfile=`eval $findfile`
events=`echo "clientevents_"$1"_by_minute_"$frompretty"_to_"$topretty`
findfile="find /opt/cloudant-performancecollector/results -name "$events"* | tail -n 1"
eventsfile=`eval $findfile`
if [ $1 = "client" ]
then
bysourcefile=`echo "/opt/cloudant-performancecollector/results/bysource_"$today".csv"`
tmpstatsfile=`echo "/opt/cloudant-performancecollector/results/tmp_client_stats"`
if [  ! -f $bysourcefile ]; then
echo "sourceip,timestamp,epoch,database_response_time_avg,cloudant_requests,e2e_response_time_avg" > $bysourcefile
fi
cat $statsfile | sed "1 d" > $tmpstatsfile
cat $statsfile | cut -d',' -f 4,5,6,18,20,23 | sed "1 d" >> $bysourcefile
dynatracefile=`echo "/opt/cloudant-performancecollector/results/bysource_dynatrace.sh"`
touch $dynatracefile
truncate --size 0 $dynatracefile
while read -r line 
do
sourceip=`echo "$line" | cut -d',' -f 4`
epoch=`echo "$line"  | cut -d',' -f 6`
cloudantdatabaseresponsetimeavg=`echo "$line" | cut -d',' -f 18`
cloudantrequests=`echo "$line"  | cut -d',' -f 20`
cloudante2eresponsetimeavg=`echo "$line"  | cut -d',' -f 23`
dynatrace_ingest=`echo "/opt/dynatrace/oneagent/agent/tools/dynatrace_ingest"`
echo "$dynatrace_ingest -v 'cloudantclient.database_response_time,sourceip=$sourceip $cloudantdatabaseresponsetimeavg $epoch""000'" >> $dynatracefile
echo "$dynatrace_ingest -v 'cloudantclient.requests,sourceip=$sourceip $cloudantrequests $epoch""000'" >> $dynatracefile
echo "$dynatrace_ingest -v 'cloudantclient.e2e_response_time,sourceip=$sourceip $cloudante2eresponsetimeavg $epoch""000'" >> $dynatracefile
done <$tmpstatsfile
chmod +x /opt/cloudant-performancecollector/results/bysource_dynatrace.sh
#/opt/cloudant-performancecollector/results/bysource_dynatrace.sh > /var/log/bysource_dynatrace.log
fi
rm -f $statsfile $eventsfile $tmpstatsfile 

