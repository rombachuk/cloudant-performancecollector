#!/bin/bash
# set -x
now=`date +%s`
smooshfindfile="find /opt/cloudant-performancecollector/results -name smooshstats_$1* | tail -n 1"
smooshstatsfile=`eval $smooshfindfile`
ioqfindfile="find /opt/cloudant-performancecollector/results -name ioqtypestats_$1* | tail -n 1"
ioqstatsfile=`eval $ioqfindfile`
hostfindfile="find /opt/cloudant-performancecollector/results -name hoststats_$1* | tail -n 1"
hoststatsfile=`eval $hostfindfile`
smooshpsqlfile=`echo "/opt/cloudant-performancecollector/tmp/"$now"smooshrunner.sql"`
ioqpsqlfile=`echo "/opt/cloudant-performancecollector/tmp/"$now"ioqrunner.sql"`
hostpsqlfile=`echo "/opt/cloudant-performancecollector/tmp/"$now"hostrunner.sql"`
smooshcols=`head -1 $smooshstatsfile`
ioqcols=`head -1 $ioqstatsfile`
hostcols=`head -1 $hoststatsfile`
smooshbldpsqlfile=`echo "echo copy smoosh_stats \($smooshcols\) from \'"$smooshstatsfile"\' delimiter \',\' csv header > "$smooshpsqlfile`
eval $smooshbldpsqlfile
ioqbldpsqlfile=`echo "echo copy ioq_stats \($ioqcols\) from \'"$ioqstatsfile"\' delimiter \',\' csv header > "$ioqpsqlfile`
eval $ioqbldpsqlfile
hostbldpsqlfile=`echo "echo copy host_stats \($hostcols\) from \'"$hoststatsfile"\' delimiter \',\' csv header> "$hostpsqlfile`
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
