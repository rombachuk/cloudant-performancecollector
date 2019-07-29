#!/bin/bash
# set -x
source /opt/cloudant-performancecollector/venv/bin/activate
stats=`echo "clientstats_"$1"_by_minute_"$2"_to_"$3`
conninfo=`echo "/opt/cloudant-performancecollector/resources/collect/configuration/perfagent_connection.info"`
/opt/cloudant-performancecollector/venv/bin/python /opt/cloudant-performancecollector/clientdata_collect.py -O csv -s $1 -g minute -f $2 -t $3 -L $4 -H $HOSTNAME -x $conninfo
