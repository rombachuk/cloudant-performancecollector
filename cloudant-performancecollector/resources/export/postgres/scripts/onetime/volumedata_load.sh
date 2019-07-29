#!/bin/bash
# set -x
now=`date +%s`
dbfindfile="find /opt/cloudant-performancecollector/results -name dbvolumestats_$1* | tail -n 1"
dbstatsfile=`eval $dbfindfile`
viewfindfile="find /opt/cloudant-performancecollector/results -name viewvolumestats_$1* | tail -n 1"
viewstatsfile=`eval $viewfindfile`
dbpsqlfile=`echo "/opt/cloudant-performancecollector/tmp/"$now"dbrunner.sql"`
viewpsqlfile=`echo "/opt/cloudant-performancecollector/tmp/"$now"viewrunner.sql"`
dbcols=`head -1 $dbstatsfile`
viewcols=`head -1 $viewstatsfile`
dbbldpsqlfile=`echo "echo copy db_stats \($dbcols\) from \'"$dbstatsfile"\' delimiter \',\' csv header > "$dbpsqlfile`
eval $dbbldpsqlfile
viewbldpsqlfile=`echo "echo copy view_stats \($viewcols\) from \'"$viewstatsfile"\' delimiter \',\' csv header > "$viewpsqlfile`
eval $viewbldpsqlfile
sed -i 's/copy/\\copy/' $dbpsqlfile
sed -i 's/copy/\\copy/' $viewpsqlfile
pghost=`cat /opt/cloudant-performancecollector/resources/export/postgres/configuration/perfagent_pg_db.info | cut -d ":" -f 1`
pgdb=`cat /opt/cloudant-performancecollector/resources/export/postgres/configuration/perfagent_pg_db.info | cut -d ":" -f 2`
pguser=`base64 --decode /opt/cloudant-performancecollector/resources/export/postgres/configuration/perfagent_pg_credentials.info | cut -d ":" -f 1`
PGPASSWORD=`base64 --decode /opt/cloudant-performancecollector/resources/export/postgres/configuration/perfagent_pg_credentials.info | cut -d ":" -f 2`
export PGPASSWORD
/usr/bin/psql -U $pguser -d $pgdb -h $pghost -f $dbpsqlfile 
/usr/bin/psql -U $pguser -d $pgdb -h $pghost -f $viewpsqlfile 
rm -f $dbpsqlfile $viewpsqlfile 
