#!/bin/bash
# set -x
stats=`echo "bodystats_body_by_minute_"$1"_to_"$2`
findfile="find /opt/cloudant-performancecollector/perfagent_results -name "$stats"* | tail -n 1"
statsfile=`eval $findfile`
psqlfile=`echo "/opt/cloudant-performancecollector/perfagent_cronscript/"body$2"_body_"$frompretty"runner.sql"`
datacols=`head -1 $statsfile`
bldpsqlfile=`echo "echo copy body_endpoint_stats \(index"$datacols"\) from \'"$statsfile"\' delimiter \',\' csv header > "$psqlfile`
eval $bldpsqlfile
sed -i 's/copy/\\copy/' $psqlfile
pghost=`cat /opt/cloudant-performancecollector/perfagent_pg_db.info | cut -d ":" -f 1`
pgdb=`cat /opt/cloudant-performancecollector/perfagent_pg_db.info | cut -d ":" -f 2`
pguser=`base64 --decode /opt/cloudant-performancecollector/perfagent_pg_credentials.info | cut -d ":" -f 1`
PGPASSWORD=`base64 --decode /opt/cloudant-performancecollector/perfagent_pg_credentials.info | cut -d ":" -f 2`
export PGPASSWORD
/usr/bin/psql -U $pguser -d $pgdb -h $pghost -f $psqlfile
rm -f $psqlfile 
#rm -f $statsfile $eventsfile
