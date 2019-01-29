#!/bin/bash
# set -x
nowepoch=`date +%s`
let fromepoch=$nowepoch-$2*60
let toepoch=$nowepoch-$3*60
frompretty=`date -d @$fromepoch +%Y%m%d%H%M`
fromgrep=`date -d @$fromepoch +%d/%b/%Y:%H:%M`
topretty=`date -d @$toepoch +%Y%m%d%H%M`
stats=`echo "clientstats_"$1"_by_minute_"$frompretty"_to_"$topretty`
logfile=`echo "/opt/cloudant-performancecollector/perfagent_cronscript/"client$HOSTNAME"_"$1"_"$frompretty"_haproxy.log"`
tail -n 500000 /var/log/haproxy.log | grep $fromgrep > $logfile
conninfo=`echo "/opt/cloudant-performancecollector/perfagent_connection.info"`
/usr/bin/python /opt/cloudant-performancecollector/clientdata_collect.py -O csv -s $1 -g minute -f $frompretty -t $topretty -L $logfile -H $HOSTNAME -x $conninfo
findfile="find /opt/cloudant-performancecollector/perfagent_results -name "$stats"* | tail -n 1"
statsfile=`eval $findfile`
eventsfile=`echo $statsfile |sed s/stats_/events_/`
psqlfile=`echo "/opt/cloudant-performancecollector/perfagent_cronscript/"client$HOSTNAME"_"$1"_"$frompretty"runner.sql"`
if [ $1 == "all" ]; then
 scopecols="cluster,loghost"
elif [ $1 == "client" ]; then
 scopecols="cluster,loghost,client"
elif [ $1 == "verb" ]; then
 scopecols="cluster,loghost,client,verb"
elif [ $1 == "endpoint" ]; then
 scopecols="cluster,loghost,client,verb,endpoint"
else
 scopecols="cluster,loghost"
fi
bldpsqlfile=`echo "echo copy "client_$1"_stats \(index,"$scopecols",mtime,mtime_epoch,tqmin,tqavg,tqmax,tqcount,tqsum,trmin,travg,trmax,trcount,trsum,ttmin,ttavg,ttmax,ttcount,ttsum,ttrmin,ttravg,ttrmax,ttrcount,ttrsum,szmin,szavg,szmax,szcount,szsum,st2count,st3count,st4count,st5count,stfailpct\) from \'"$statsfile"\' delimiter \',\' csv header > "$psqlfile`
eval $bldpsqlfile
sed -i 's/copy/\\copy/' $psqlfile
pghost=`cat /opt/cloudant-performancecollector/perfagent_pg_db.info | cut -d ":" -f 1`
pgdb=`cat /opt/cloudant-performancecollector/perfagent_pg_db.info | cut -d ":" -f 2`
pguser=`base64 --decode /opt/cloudant-performancecollector/perfagent_pg_credentials.info | cut -d ":" -f 1`
PGPASSWORD=`base64 --decode /opt/cloudant-performancecollector/perfagent_pg_credentials.info | cut -d ":" -f 2`
export PGPASSWORD
/usr/bin/psql -U $pguser -d $pgdb -h $pghost -f $psqlfile
rm -f $psqlfile $logfile  $statsfile $eventsfile
