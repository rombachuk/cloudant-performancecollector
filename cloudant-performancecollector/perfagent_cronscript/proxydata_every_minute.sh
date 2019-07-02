#!/bin/bash 
# set -x
nowepoch=`date +%s`
let fromepoch=$nowepoch-$2*60
let toepoch=$nowepoch-$3*60
frompretty=`date -d @$fromepoch +%Y%m%d%H%M`
topretty=`date -d @$toepoch +%Y%m%d%H%M`
/opt/cloudant-performancecollector/perfagent_cronscript/proxydata_minute_onetime.sh $1 $frompretty $topretty $4
