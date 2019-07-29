#!/bin/bash
# set -x
stats=`echo "bodystats_"$1"_by_"$2"_"$3"_to_"$4`
findfile="find /opt/cloudant-performancecollector/results -name "$stats"* | tail -n 1"
statsfile=`eval $findfile`
psqlfile=`echo "/opt/cloudant-performancecollector/tmp/"body$3"_body_"$4"runner.sql"`
datacols=`head -1 $statsfile`
if [ "$2" == "second" ]
 then
  table="body_endpoint_stats_s"
 else
  table="body_endpoint_stats"
fi  
bldpsqlfile=`echo "echo copy "$table" \(index"$datacols"\) from \'"$statsfile"\' delimiter \',\' csv header > "$psqlfile`
eval $bldpsqlfile
sed -i 's/copy/\\copy/' $psqlfile
pghost=`cat /opt/cloudant-performancecollector/resources/export/postgres/configuration/perfagent_pg_db.info | cut -d ":" -f 1`
pgdb=`cat /opt/cloudant-performancecollector/resources/export/postgres/configuration/perfagent_pg_db.info | cut -d ":" -f 2`
pguser=`base64 --decode /opt/cloudant-performancecollector/resources/export/postgres/configuration/perfagent_pg_credentials.info | cut -d ":" -f 1`
PGPASSWORD=`base64 --decode /opt/cloudant-performancecollector/resources/export/postgres/configuration/perfagent_pg_credentials.info | cut -d ":" -f 2`
export PGPASSWORD
/usr/bin/psql -U $pguser -d $pgdb -h $pghost -f $psqlfile
rm -f $psqlfile 
#rm -f $statsfile $eventsfile
