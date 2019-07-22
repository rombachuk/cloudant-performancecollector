#!/bin/bash
# set -x
now=`date +%s`
smooshfindfile="find /opt/cloudant-performancecollector/results -name smooshcompactionstats* | tail -n 1"
smooshstatsfile=`eval $smooshfindfile`
ioqfindfile="find /opt/cloudant-performancecollector/results -name ioqcompactionstats* | tail -n 1"
ioqstatsfile=`eval $ioqfindfile`
hostfindfile="find /opt/cloudant-performancecollector/results -name hostcompactionstats* | tail -n 1"
hoststatsfile=`eval $hostfindfile`
smooshpsqlfile=`echo "/opt/cloudant-performancecollector/tmp/"$now"smooshrunner.sql"`
ioqpsqlfile=`echo "/opt/cloudant-performancecollector/tmp/"$now"ioqrunner.sql"`
hostpsqlfile=`echo "/opt/cloudant-performancecollector/tmp/"$now"hostrunner.sql"`
smooshbldpsqlfile=`echo "echo copy smoosh_stats \(index,cluster,host,channel,mtime,mtime_epoch,active,waiting,starting\) from \'"$smooshstatsfile"\' delimiter \',\' csv > "$smooshpsqlfile`
eval $smooshbldpsqlfile
ioqbldpsqlfile=`echo "echo copy ioq_stats \(index,cluster,host,ioqtype,mtime,mtime_epoch,requests\) from \'"$ioqstatsfile"\' delimiter \',\' csv > "$ioqpsqlfile`
eval $ioqbldpsqlfile
hostbldpsqlfile=`echo "echo copy host_stats \(index,cluster,host,mtime,mtime_epoch,doc_writes,doc_inserts,ioql_max,ioql_med,ioql_pctl_90,ioql_pctl_99,ioql_pctl_999\) from \'"$hoststatsfile"\' delimiter \',\' csv > "$hostpsqlfile`
eval $hostbldpsqlfile
sed -i 's/copy/\\copy/' $smooshpsqlfile
sed -i 's/copy/\\copy/' $ioqpsqlfile
sed -i 's/copy/\\copy/' $hostpsqlfile
pghost=`cat /opt/cloudant-performancecollector/resources/export/postgres/configuration/perfagent_pg_db.info | cut -d ":" -f 1`
pgdb=`cat /opt/cloudant-performancecollector/resources/export/postgres/configuration/perfagent_pg_db.info | cut -d ":" -f 2`
pguser=`base64 --decode /opt/cloudant-performancecollector/resources/export/postgres/configuration/perfagent_pg_credentials.info | cut -d ":" -f 1`
PGPASSWORD=`base64 --decode /opt/cloudant-performancecollector/resources/export/postgres/configuration/perfagent_pg_credentials.info | cut -d ":" -f 2`
export PGPASSWORD

/usr/bin/psql -U $pguser -d $pgdb -h $pghost -f $smooshpsqlfile 
/usr/bin/psql -U $pguser -d $pgdb -h $pghost -f $ioqpsqlfile 
/usr/bin/psql -U $pguser -d $pgdb -h $pghost -f $hostpsqlfile 
rm -f $smooshpsqlfile $ioqpsqlfile $hostpsqlfile
#rm -f $smooshstatsfile $ioqstatsfile $hoststatsfile
