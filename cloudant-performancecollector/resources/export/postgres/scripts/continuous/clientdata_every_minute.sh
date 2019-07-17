#!/bin/bash 
# set -x
nowepoch=`date +%s`
let fromepoch=$nowepoch-$2*60
let toepoch=$nowepoch-$3*60
frompretty=`date -d @$fromepoch +%Y%m%d%H%M`
topretty=`date -d @$toepoch +%Y%m%d%H%M`
fromgrep=`date -d @$fromepoch +%d/%b/%Y:%H:%M`
logfile=`echo "/opt/cloudant-performancecollector/tmp/"client$HOSTNAME"_"$1"_"$frompretty"_haproxy.log.gz"`
tail -n 500000 /var/log/haproxy.log | grep $fromgrep | gzip > $logfile
/opt/cloudant-performancecollector/resources/collect/scripts/clientdata_minute_collect.sh $1 $frompretty $topretty $logfile
/opt/cloudant-performancecollector/resources/export/postgres/scripts/onetime/clientdata_minute_load.sh $1 $frompretty $topretty