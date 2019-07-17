#!/bin/bash
# set -x
stats=`echo "stats_"$1"_by_minute_"$2"_to_"$3`
findfile="find /opt/cloudant-performancecollector/results -name "$stats"* | tail -n 1"
statsfile=`eval $findfile`
psqlfile=`echo "/opt/cloudant-performancecollector/tmp/"$1"_"$2"runner.sql"`
datacols=`head -1 $statsfile`
bldpsqlfile=`echo "echo copy "$1"_stats \(index"$datacols"\) from \'"$statsfile"\' delimiter \',\' csv header > "$psqlfile`
eval $bldpsqlfile
sed -i 's/copy/\\copy/' $psqlfile
pghost=`cat /opt/cloudant-performancecollector/resources/export/postgres/configuration/perfagent_pg_db.info | cut -d ":" -f 1`
pgdb=`cat /opt/cloudant-performancecollector/resources/export/postgres/configuration/perfagent_pg_db.info | cut -d ":" -f 2`
pguser=`base64 --decode /opt/cloudant-performancecollector/resources/export/postgres/configuration/perfagent_pg_credentials.info | cut -d ":" -f 1`
PGPASSWORD=`base64 --decode /opt/cloudant-performancecollector/resources/export/postgres/configuration/perfagent_pg_credentials.info | cut -d ":" -f 2`
export PGPASSWORD
/usr/bin/psql -U $pguser -d $pgdb -h $pghost -f $psqlfile
rm -f $psqlfile 
rm $statsfile $eventsfile
