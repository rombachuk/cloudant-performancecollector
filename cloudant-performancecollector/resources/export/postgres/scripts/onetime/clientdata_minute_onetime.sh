#!/bin/bash
# set -x
/opt/cloudant-performancecollector/resources/collect/scripts/clientdata_minute_collect.sh $1 $2 $3 $4 
/opt/cloudant-performancecollector/resources/export/postgres/scripts/onetime/clientdata_minute_load.sh $1 $2 $3 
