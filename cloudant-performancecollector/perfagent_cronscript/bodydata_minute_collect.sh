#!/bin/bash
# set -x
stats=`echo "bodystats_body_by_minute_"$1"_to_"$2`
conninfo=`echo "/opt/cloudant-performancecollector/perfagent_connection.info"`
/usr/bin/python /opt/cloudant-performancecollector/bodydata_collect.py -O csv -s body -g minute -f $1 -t $2 -L $4 -H $3 -x $conninfo
