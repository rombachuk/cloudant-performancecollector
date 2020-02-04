#!/bin/bash
# set -x
/opt/cloudant-performancecollector/resources/collect/scripts/bodydata_second_collect.sh $1 $2 $3 
/opt/cloudant-performancecollector/resources/export/postgres/scripts/onetime/bodydata_second_load.sh $1 $2  
