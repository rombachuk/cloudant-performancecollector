#!/bin/bash
# set -x
stats=`echo "bodystats_body_by_minute_"$1"_to_"$2`
findfile="find /opt/cloudant-performancecollector/perfagent_results -name "$stats"* | tail -n 1"
statsfile=`eval $findfile`
psqlfile=`echo "/opt/cloudant-performancecollector/perfagent_cronscript/"body$2"_body_"$frompretty"runner.sql"`
bldpsqlfile=`echo "echo copy body_endpoint_stats \(index,cluster,loghost,client,database,verb,endpoint,body,mtime,mtime_epoch,tqmin,tqavg,tqmax,tqcount,tqsum,trmin,travg,trmax,trcount,trsum,ttmin,ttavg,ttmax,ttcount,ttsum,ttrmin,ttravg,ttrmax,ttrcount,ttrsum,szmin,szavg,szmax,szcount,szsum,st2count,st3count,st4count,st5count,stfailpct\) from \'"$statsfile"\' delimiter \',\' csv header > "$psqlfile`
eval $bldpsqlfile
sed -i 's/copy/\\copy/' $psqlfile
pghost=`cat /opt/cloudant-performancecollector/perfagent_pg_db.info | cut -d ":" -f 1`
pgdb=`cat /opt/cloudant-performancecollector/perfagent_pg_db.info | cut -d ":" -f 2`
pguser=`base64 --decode /opt/cloudant-performancecollector/perfagent_pg_credentials.info | cut -d ":" -f 1`
PGPASSWORD=`base64 --decode /opt/cloudant-performancecollector/perfagent_pg_credentials.info | cut -d ":" -f 2`
export PGPASSWORD
/usr/bin/psql -U $pguser -d $pgdb -h $pghost -f $psqlfile
rm -f $psqlfile $statsfile $eventsfile
