#!/bin/bash 
# set -x
nowepoch=`date +%s`
let fromepoch=$nowepoch-$2*60
let toepoch=$nowepoch-$3*60
frompretty=`date -d @$fromepoch +%Y%m%d%H%M`
topretty=`date -d @$toepoch +%Y%m%d%H%M`
/opt/cloudant-performancecollector/resources/collect/scripts/metricsdbdata_collect.sh 
/opt/cloudant-performancecollector/resources/export/postgres/scripts/onetime/metricsdbdata_load.sh
smooshfindfile="find /opt/cloudant-performancecollector/results -name smooshcompactionstats* | tail -n 1"
smooshstatsfile=`eval $smooshfindfile`
ioqfindfile="find /opt/cloudant-performancecollector/results -name ioqcompactionstats* | tail -n 1"
ioqstatsfile=`eval $ioqfindfile`
hostfindfile="find /opt/cloudant-performancecollector/results -name hostcompactionstats* | tail -n 1"
hoststatsfile=`eval $hostfindfile`
rm -f $smooshstatsfile $ioqstatsfile $hoststatsfile
