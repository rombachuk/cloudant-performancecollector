#!/bin/bash 
# set -x
nowepoch=`date +%s`
let fromepoch=$nowepoch
frompretty=`date -d @$fromepoch +%Y%m%d%H%M`
/opt/cloudant-performancecollector/resources/collect/scripts/metricsdbdata_collect.sh $frompretty 
/opt/cloudant-performancecollector/resources/export/postgres/scripts/onetime/metricsdbdata_load.sh $frompretty
smooshfindfile="find /opt/cloudant-performancecollector/results -name smooshstats_$frompretty_* | tail -n 1"
smooshstatsfile=`eval $smooshfindfile`
ioqfindfile="find /opt/cloudant-performancecollector/results -name ioqtypestats_$frompretty_* | tail -n 1"
ioqstatsfile=`eval $ioqfindfile`
hostfindfile="find /opt/cloudant-performancecollector/results -name hoststats_$frompretty_* | tail -n 1"
hoststatsfile=`eval $hostfindfile`
rm -f $smooshstatsfile $ioqstatsfile $hoststatsfile
