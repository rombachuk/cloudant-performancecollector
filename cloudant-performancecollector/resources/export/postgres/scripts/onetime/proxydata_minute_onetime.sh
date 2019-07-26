#!/bin/bash
# set -x
/opt/cloudant-performancecollector/resources/collect/scripts/proxydata_minute_collect.sh $1 $2 $3 $4 
/opt/cloudant-performancecollector/resources/export/postgres/scripts/onetime/proxydata_minute_load.sh $1 $2 $3 
