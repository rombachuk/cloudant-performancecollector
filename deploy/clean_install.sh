#!/bin/bash
now=`date +%Y%m%d%H%M`
systemctl stop cpc_api_processor
cp -r /opt/cloudant-performancecollector /opt/cloudant-performancecollector-bkp-$now
mkdir /opt/cloudant-performancecollector-bkp-$now/init.d
cp /etc/init.d/cpc_api_processor /opt/cloudant-performancecollector-bkp-$now/init.d
rm -rf /opt/cloudant-performancecollector
rm -f /etc/init.d/cpc_api_processor
cp -r ../cloudant-performancecollector /opt
cp /opt/cloudant-performancecollector/cpc_api_processor /etc/init.d
systemctl enable cpc_api_processor
systemctl start cpc_api_processor
read -p 'Drop and recreate postgres schema (y/n): ' confirm
if [ "$confirm" == "y" ]
then
 if [[ -z $1 ]]
 then
  read -p 'Postgres Host: ' host
 else
 host=$1
 fi
 if [[ -z $2 ]]
 then
  read -sp 'Postgres Cloudant password: ' cpwd
 else
  cpwd=$2
 fi
 export PGPASSWORD=$cpwd
 echo 'dropping existing postgres proxydata schema'
 /usr/bin/psql -U cloudant -d postgres -h $host -f ../cloudant-performancecollector/proxydata_postgres_drop.sql -o schema_drop.log
 echo 'creating new postgres proxydata schema'
 /usr/bin/psql -U cloudant -d postgres -h $host -f ../cloudant-performancecollector/proxydata_postgres.sql -o schema_create.log
 echo 'dropping existing postgres metricsdb-data schema'
 /usr/bin/psql -U cloudant -d postgres -h $host -f ../cloudant-performancecollector/metricsdbdata_postgres_drop.sql -o schema_drop.log
 echo 'creating new postgres metricsdb-data schema'
 /usr/bin/psql -U cloudant -d postgres -h $host -f ../cloudant-performancecollector/metricsdbdata_postgres.sql -o schema_create.log
else
 echo 'no postgres schema changes'
fi
echo 'completed'