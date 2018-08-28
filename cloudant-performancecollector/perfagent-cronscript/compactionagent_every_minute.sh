#!/bin/bash
# set -x
now=`date +%s`
/usr/bin/python /opt/cloudant-specialapi/compactionagent.py -x $2
sleep 5
dbfindfile="find /opt/cloudant-specialapi/perfagent_results -name dbcompactionstats* | tail -n 1"
dbstatsfile=`eval $dbfindfile`
viewfindfile="find /opt/cloudant-specialapi/perfagent_results -name viewcompactionstats* | tail -n 1"
viewstatsfile=`eval $viewfindfile`
smooshfindfile="find /opt/cloudant-specialapi/perfagent_results -name smooshcompactionstats* | tail -n 1"
smooshstatsfile=`eval $smooshfindfile`
ioqfindfile="find /opt/cloudant-specialapi/perfagent_results -name ioqcompactionstats* | tail -n 1"
ioqstatsfile=`eval $ioqfindfile`
hostfindfile="find /opt/cloudant-specialapi/perfagent_results -name hostcompactionstats* | tail -n 1"
hoststatsfile=`eval $hostfindfile`
dbpsqlfile=`echo "/opt/cloudant-specialapi/perfagent_cronscript/"$now"dbrunner.sql"`
viewpsqlfile=`echo "/opt/cloudant-specialapi/perfagent_cronscript/"$now"viewrunner.sql"`
smooshpsqlfile=`echo "/opt/cloudant-specialapi/perfagent_cronscript/"$now"smooshrunner.sql"`
ioqpsqlfile=`echo "/opt/cloudant-specialapi/perfagent_cronscript/"$now"ioqrunner.sql"`
hostpsqlfile=`echo "/opt/cloudant-specialapi/perfagent_cronscript/"$now"hostrunner.sql"`
dbbldpsqlfile=`echo "echo copy db_stats \(index,cluster,database,mtime,mtime_epoch,doc_count,del_doc_count,disk_size,data_size\) from \'"$dbstatsfile"\' delimiter \',\' csv > "$dbpsqlfile`
eval $dbbldpsqlfile
viewbldpsqlfile=`echo "echo copy view_stats \(index,cluster,database,viewdoc,view,signature,mtime,mtime_epoch,disk_size,data_size,active_size,updates_pending_total,updates_pending_minimum,updates_pending_preferred\) from \'"$viewstatsfile"\' delimiter \',\' csv > "$viewpsqlfile`
eval $viewbldpsqlfile
smooshbldpsqlfile=`echo "echo copy smoosh_stats \(index,cluster,host,channel,mtime,mtime_epoch,active,waiting,starting\) from \'"$smooshstatsfile"\' delimiter \',\' csv > "$smooshpsqlfile`
eval $smooshbldpsqlfile
ioqbldpsqlfile=`echo "echo copy ioq_stats \(index,cluster,host,ioqtype,mtime,mtime_epoch,requests\) from \'"$ioqstatsfile"\' delimiter \',\' csv > "$ioqpsqlfile`
eval $ioqbldpsqlfile
hostbldpsqlfile=`echo "echo copy host_stats \(index,cluster,host,mtime,mtime_epoch,doc_writes,doc_inserts,ioql_max,ioql_med,ioql_pctl_90,ioql_pctl_99,ioql_pctl_999\) from \'"$hoststatsfile"\' delimiter \',\' csv > "$hostpsqlfile`
eval $hostbldpsqlfile
sed -i 's/copy/\\copy/' $dbpsqlfile
sed -i 's/copy/\\copy/' $viewpsqlfile
sed -i 's/copy/\\copy/' $smooshpsqlfile
sed -i 's/copy/\\copy/' $ioqpsqlfile
sed -i 's/copy/\\copy/' $hostpsqlfile
PGPASSWORD=cloudant
export PGPASSWORD
/usr/bin/psql -U cloudant -d postgres -h $1 -f $dbpsqlfile 
/usr/bin/psql -U cloudant -d postgres -h $1 -f $viewpsqlfile 
/usr/bin/psql -U cloudant -d postgres -h $1 -f $smooshpsqlfile 
/usr/bin/psql -U cloudant -d postgres -h $1 -f $ioqpsqlfile 
/usr/bin/psql -U cloudant -d postgres -h $1 -f $hostpsqlfile 
rm -f $dbpsqlfile $viewpsqlfile $smooshpsqlfile $ioqpsqlfile $hostpsqlfile
rm -f $viewstatsfile $dbstatsfile $smooshstatsfile $ioqstatsfile $hoststatsfile
