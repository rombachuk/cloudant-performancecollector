#!/bin/bash
# set -x
nowepoch=`date +%s`
let fromepoch=$nowepoch-$2*60
let toepoch=$nowepoch-$3*60
frompretty=`date -d @$fromepoch +%Y%m%d%H%M`
fromgrep=`date -d @$fromepoch +%d/%b/%Y:%H:%M`
topretty=`date -d @$toepoch +%Y%m%d%H%M`
stats=`echo "stats_"$1"_by_minute_"$frompretty"_to_"$topretty`
logfile=`echo "/opt/cloudant-specialapi/perfagent_cronscript/"$4"_"$1"_"$frompretty"_haproxy.log"`
tail -n 500000 /var/log/haproxy.log | grep $fromgrep > $logfile
/usr/bin/python /opt/cloudant-specialapi/perfagent.py -O csv -s $1 -g minute -f $frompretty -t $topretty -L $logfile -H $5 -x $6
findfile="find /opt/cloudant-specialapi/perfagent_results -name "$stats"* | tail -n 1"
statsfile=`eval $findfile`
eventsfile=`echo $statsfile |sed s/stats_/events_/`
psqlfile=`echo "/opt/cloudant-specialapi/perfagent_cronscript/"$4"_"$1"_"$frompretty"runner.sql"`
if [ $1 == "all" ]; then
 scopecols="cluster,loghost"
elif [ $1 == "database" ]; then
 scopecols="cluster,loghost,database"
elif [ $1 == "verb" ]; then
 scopecols="cluster,loghost,database,verb"
elif [ $1 == "endpoint" ]; then
 scopecols="cluster,loghost,database,verb,endpoint"
elif [ $1 == "document" ]; then
 scopecols="cluster,loghost,database,verb,endpoint,document"
else
 scopecols="cluster,loghost"
fi
bldpsqlfile=`echo "echo copy "$1"_stats \(index,"$scopecols",mtime,mtime_epoch,tqmin,tqavg,tqmax,tqcount,tqsum,trmin,travg,trmax,trcount,trsum,ttmin,ttavg,ttmax,ttcount,ttsum,ttrmin,ttravg,ttrmax,ttrcount,ttrsum,szmin,szavg,szmax,szcount,szsum,st2count,st3count,st4count,st5count,stfailpct\) from \'"$statsfile"\' delimiter \',\' csv header > "$psqlfile`
eval $bldpsqlfile
sed -i 's/copy/\\copy/' $psqlfile
PGPASSWORD=cloudant
export PGPASSWORD
/usr/bin/psql -U cloudant -d postgres -h $4 -f $psqlfile 
rm -f $psqlfile $logfile  $statsfile $eventsfile 
