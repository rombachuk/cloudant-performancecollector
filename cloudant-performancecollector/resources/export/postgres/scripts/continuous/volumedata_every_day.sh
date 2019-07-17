#!/bin/bash
# set -x
now=`date +%s`
conninfo=`echo "/opt/cloudant-performancecollector/perfagent_connection.info"`
/usr/bin/python /opt/cloudant-performancecollector/volume_collect.py -x $conninfo
sleep 5
dbfindfile="find /opt/cloudant-performancecollector/perfagent_results -name dbvolumestats* | tail -n 1"
dbstatsfile=`eval $dbfindfile`
viewfindfile="find /opt/cloudant-performancecollector/perfagent_results -name viewvolumestats* | tail -n 1"
viewstatsfile=`eval $viewfindfile`
dbpsqlfile=`echo "/opt/cloudant-performancecollector/perfagent_cronscript/"$now"dbrunner.sql"`
viewpsqlfile=`echo "/opt/cloudant-performancecollector/perfagent_cronscript/"$now"viewrunner.sql"`
dbbldpsqlfile=`echo "echo copy db_stats \(index,cluster,database,mtime,mtime_epoch,doc_count,del_doc_count,disk_size,data_size,shard_count\) from \'"$dbstatsfile"\' delimiter \',\' csv > "$dbpsqlfile`
eval $dbbldpsqlfile
viewbldpsqlfile=`echo "echo copy view_stats \(index,cluster,database,viewdoc,view,signature,mtime,mtime_epoch,disk_size,data_size,active_size,updates_pending_total,updates_pending_minimum,updates_pending_preferred,shard_count\) from \'"$viewstatsfile"\' delimiter \',\' csv > "$viewpsqlfile`
eval $viewbldpsqlfile
sed -i 's/copy/\\copy/' $dbpsqlfile
sed -i 's/copy/\\copy/' $viewpsqlfile
pghost=`cat /opt/cloudant-performancecollector/perfagent_pg_db.info | cut -d ":" -f 1`
pgdb=`cat /opt/cloudant-performancecollector/perfagent_pg_db.info | cut -d ":" -f 2`
pguser=`base64 --decode /opt/cloudant-performancecollector/perfagent_pg_credentials.info | cut -d ":" -f 1`
PGPASSWORD=`base64 --decode /opt/cloudant-performancecollector/perfagent_pg_credentials.info | cut -d ":" -f 2`
export PGPASSWORD
/usr/bin/psql -U $pguser -d $pgdb -h $pghost -f $dbpsqlfile 
/usr/bin/psql -U $pguser -d $pgdb -h $pghost -f $viewpsqlfile 
rm -f $dbpsqlfile $viewpsqlfile 
rm -f $viewstatsfile $dbstatsfile 
