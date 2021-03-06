#!/bin/bash 
# set -x
source /opt/cloudant-performancecollector/venv/bin/activate
nowepoch=`date +%s`
let fromepoch=$nowepoch
frompretty=`date -d @$fromepoch +%Y%m%d%H%M`
/opt/cloudant-performancecollector/resources/collect/scripts/volumedata_collect.sh $frompretty 
/opt/cloudant-performancecollector/venv/bin/python /opt/cloudant-performancecollector/es_exporter.py -d volume -f $frompretty
dbfindfile="find /opt/cloudant-performancecollector/results -name dbvolumestats_$frompretty_* | tail -n 1"
dbstatsfile=`eval $dbfindfile`
viewfindfile="find /opt/cloudant-performancecollector/results -name viewvolumestats_$frompretty_* | tail -n 1"
viewstatsfile=`eval $viewfindfile`
rm -f $dbstatsfile $viewstatsfile
