#!/bin/bash
# set -x
now=`date +%s`
/usr/bin/python /opt/cloudant-performancecollector/volume_collect.py -x $2
sleep 5
dbfindfile="find /opt/cloudant-performancecollector/perfagent_results -name dbvolumestats* | tail -n 1"
dbstatsfile=`eval $dbfindfile`
viewfindfile="find /opt/cloudant-performancecollector/perfagent_results -name viewvolumestats* | tail -n 1"
viewstatsfile=`eval $viewfindfile`
dbpsqlfile=`echo "/opt/cloudant-performancecollector/perfagent_cronscript/"$now"dbrunner.sql"`
viewpsqlfile=`echo "/opt/cloudant-performancecollector/perfagent_cronscript/"$now"viewrunner.sql"`
dbbldpsqlfile=`echo "echo copy db_stats \(index,cluster,database,mtime,mtime_epoch,doc_count,del_doc_count,disk_size,data_size\) from \'"$dbstatsfile"\' delimiter \',\' csv > "$dbpsqlfile`
eval $dbbldpsqlfile
viewbldpsqlfile=`echo "echo copy view_stats \(index,cluster,database,viewdoc,view,signature,mtime,mtime_epoch,disk_size,data_size,active_size,updates_pending_total,updates_pending_minimum,updates_pending_preferred\) from \'"$viewstatsfile"\' delimiter \',\' csv > "$viewpsqlfile`
eval $viewbldpsqlfile
sed -i 's/copy/\\copy/' $dbpsqlfile
sed -i 's/copy/\\copy/' $viewpsqlfile
PGPASSWORD=cloudant
export PGPASSWORD
/usr/bin/psql -U cloudant -d postgres -h $1 -f $dbpsqlfile 
/usr/bin/psql -U cloudant -d postgres -h $1 -f $viewpsqlfile 
rm -f $dbpsqlfile $viewpsqlfile 
rm -f $viewstatsfile $dbstatsfile 
