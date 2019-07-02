#!/bin/bash
# set -x
/opt/cloudant-performancecollector/perfagent_cronscript/proxydata_minute_collect.sh $1 $2 $3 $4 
/opt/cloudant-performancecollector/perfagent_cronscript/proxydata_minute_load.sh $1 $2 $3 
