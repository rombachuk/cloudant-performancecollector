#!/bin/bash
# set -x
source /opt/cloudant-performancecollector/venv/bin/activate
stats=`echo "bodystats_body_by_minute_"$1"_to_"$2`
conninfo=`echo "/opt/cloudant-performancecollector/resources/collect/configuration/perfagent_connection.info"`
/opt/cloudant-performancecollector/venv/bin/python /opt/cloudant-performancecollector/bodydata_collect.py -O csv -s body -g minute -f $1 -t $2 -L $3 -H $HOSTNAME -x $conninfo
