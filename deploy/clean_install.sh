#!/bin/bash
now=`date +%Y%m%d%H%M` 
systemctl stop cpc_api_processor
cp -r /opt/cloudant-performancecollector /opt/cloudant-performancecollector-bkp-$now
mkdir /opt/cloudant-performancecollector-bkp-$now/init.d
cp /etc/init.d/cpc_api_processor /opt/cloudant-performancecollector-bkp-$now/init.d
rm -rf /opt/cloudant-performancecollector
rm -f /etc/init.d/cpc_api_processor
cp -r ../cloudant-performancecollector /opt
read -p 'Does this server have online access for pip commands (Online install) (y/n): ' confirmonline
if [ "$confirmonline" == "y" ]
then
 /usr/bin/virtualenv /opt/cloudant-performancecollector/venv
 source /opt/cloudant-performancecollector/venv/bin/activate
 pip install requests
 pip install elasticsearch
 pip install pandas
 pip install flask
else
 read -p 'Do you really want to perform offline install (y/n): ' confirmoffline
 if [ "$confirmoffline" == "y" ]
 then
 cp ../offline/wheelhouse.tar.gz /opt/cloudant-performancecollector
 cd /opt/cloudant-performancecollector
 /usr/bin/tar xzvf /opt/cloudant-performancecollector/wheelhouse.tar.gz
 /usr/bin/virtualenv /opt/cloudant-performancecollector/venv
 source /opt/cloudant-performancecollector/venv/bin/activate
 cd /opt/cloudant-performancecollector/wheelhouse
 /opt/cloudant-performancecollector/venv/bin/python pip-19.2.1-py2.py3-none-any.whl/pip install --no-index pip-19.2.1-py2.py3-none-any.whl setuptools-41.0.1-py2.py3-none-any.whl
 pip install -r /opt/cloudant-performancecollector/wheelhouse/requirements.txt --no-index --find-links /opt/cloudant-performancecollector/wheelhouse
 cd -
 fi
fi
cp /opt/cloudant-performancecollector/resources/collect/scripts/cpc_api_processor /etc/init.d
systemctl enable cpc_api_processor
systemctl start cpc_api_processor
read -p 'Export to Elasticsearch (y/n): ' confirmes
if [ "$confirmes" == "y" ]
then
read -p 'Drop and recreate elasticsearch templates (y/n): ' confirmesschema
if [ "$confirmesschema" == "y" ]
then
 /opt/cloudant-performancecollector/resources/export/elasticsearch/schema/template_install.sh
fi
fi
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
