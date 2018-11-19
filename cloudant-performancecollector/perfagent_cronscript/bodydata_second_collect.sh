#!/bin/bash
# set -x
stats=`echo "bodystats_body_by_second_"$1"_to_"$2`
/usr/bin/python /opt/cloudant-performancecollector/bodydata_collect.py -O csv -s body -g second -f $1 -t $2 -L $3 -H $4 -x $5
