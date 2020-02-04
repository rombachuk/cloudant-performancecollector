#!/bin/bash
# set -x
/opt/cloudant-performancecollector/resources/collect/scripts/bodydata_minute_collect.sh $1 $2 $3 
/opt/cloudant-performancecollector/resources/export/postgres/scripts/onetime/bodydata_minute_load.sh $1 $2  
