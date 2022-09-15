#!/bin/bash
# set -x
source /opt/cloudant-performancecollector/venv/bin/activate
stats=`echo "bodystats_"$1"_by_"$2"_"$3"_to_"$4`
conninfo=`echo "/opt/cloudant-performancecollector/resources/collect/configuration/perfagent_connection.info"`
/opt/cloudant-performancecollector/venv/bin/python3 /opt/cloudant-performancecollector/bodydata_collect.py -O csv -s $1 -g $2 -f $3 -t $4 -L $5 -H $HOSTNAME -x $conninfo
