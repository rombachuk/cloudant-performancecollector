#!/bin/bash 
# set -x
nowepoch=`date +%s`
let fromepoch=$nowepoch-$2*60
let toepoch=$nowepoch-$3*60
frompretty=`date -d @$fromepoch +%Y%m%d%H%M`
topretty=`date -d @$toepoch +%Y%m%d%H%M`
/opt/cloudant-performancecollector/resources/collect/scripts/volumedata_collect.sh 
/opt/cloudant-performancecollector/resources/export/postgres/scripts/onetime/volumedata_load.sh
