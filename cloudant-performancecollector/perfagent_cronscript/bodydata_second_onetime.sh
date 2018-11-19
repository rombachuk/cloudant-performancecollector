#!/bin/bash
# set -x
/opt/cloudant-performancecollector/perfagent_cronscript/bodydata_second_collect.sh $1 $2 $3 $4 $5
/opt/cloudant-performancecollector/perfagent_cronscript/bodydata_second_load.sh $1 $2 $4 
