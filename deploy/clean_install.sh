#!/bin/bash
now=`date +%Y%m%d%H%M` 
systemctl stop cpc_api_processor
cp -r /opt/cloudant-performancecollector /opt/cloudant-performancecollector-bkp-$now
mkdir /opt/cloudant-performancecollector-bkp-$now/init.d
cp /etc/init.d/cpc_api_processor /opt/cloudant-performancecollector-bkp-$now/init.d
rm -rf /opt/cloudant-performancecollector
rm -f /etc/init.d/cpc_api_processor
cp -r ../cloudant-performancecollector /opt
cp /opt/cloudant-performancecollector/resources/collect/scripts/cpc_api_processor /etc/init.d
systemctl enable cpc_api_processor
systemctl start cpc_api_processor
read -p 'Export to Postgres (y/n): ' confirmpg
if [ "$confirmpg" == "y" ]
then
read -p 'Drop and recreate postgres schema (y/n): ' confirmpgschema
if [ "$confirmpgschema" == "y" ]
then
 pghost=`cat /opt/cloudant-performancecollector/resources/export/postgres/configuration/perfagent_pg_db.info | cut -d ":" -f 1`
 pgdb=`cat /opt/cloudant-performancecollector/resources/export/postgres/configuration/perfagent_pg_db.info | cut -d ":" -f 2`
 pguser=`base64 --decode /opt/cloudant-performancecollector/resources/export/postgres/configuration/perfagent_pg_credentials.info | cut -d ":" -f 1`
 PGPASSWORD=`base64 --decode /opt/cloudant-performancecollector/resources/export/postgres/configuration/perfagent_pg_credentials.info | cut -d ":" -f 2`
 export PGPASSWORD
 echo 'dropping existing postgres proxydata schema'
 /usr/bin/psql -U pguser -d $pgdb -h $pghost -f ../cloudant-performancecollector/resources/export/postgres/schema/proxydata_postgres_drop.sql -o proxyschema_drop.log
 echo 'creating new postgres proxydata schema'
 /usr/bin/psql -U pguser -d $pgdb -h $pghost -f ../cloudant-performancecollector/resources/export/postgres/schema/proxydata_postgres.sql -o proxyschema_create.log
 echo 'dropping existing postgres metricsdb-data schema'
 /usr/bin/psql -U pguser -d $pgdb -h $pghost -f ../cloudant-performancecollector/resources/export/postgres/schema/metricsdbdata_postgres_drop.sql -o metricsdbschema_drop.log
 echo 'creating new postgres metricsdb-data schema'
 /usr/bin/psql -U pguser -d $pgdb -h $pghost -f ../cloudant-performancecollector/resources/export/postgres/schema/metricsdbdata_postgres.sql -o metricsdbschema_create.log
  echo 'dropping existing postgres volume-data schema'
 /usr/bin/psql -U pguser -d $pgdb -h $pghost -f ../cloudant-performancecollector/resources/export/postgres/schema/volumedata_postgres_drop.sql -o volumeschema_drop.log
 echo 'creating new postgres volume-data schema'
 /usr/bin/psql -U pguser -d $pgdb -h $pghost -f ../cloudant-performancecollector/resources/export/postgres/schema/volumedata_postgres.sql -o volumeschema_create.log
  echo 'dropping existing postgres volume-data schema'
 /usr/bin/psql -U pguser -d $pgdb -h $pghost -f ../cloudant-performancecollector/resources/export/postgres/schema/clientdata_postgres_drop.sql -o clientschema_drop.log
 echo 'creating new postgres volume-data schema'
 /usr/bin/psql -U pguser -d $pgdb -h $pghost -f ../cloudant-performancecollector/resources/export/postgres/schema/clientdata_postgres.sql -o clientschema_create.log
else
 echo 'no postgres schema changes'
fi
fi
echo 'completed'