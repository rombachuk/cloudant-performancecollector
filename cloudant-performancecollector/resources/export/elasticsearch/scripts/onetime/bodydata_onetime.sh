#!/bin/bash
# set -x
/opt/cloudant-performancecollector/resources/collect/scripts/bodydata_collect.sh $1 $2 $3  $4 $5
/usr/bin/python /opt/cloudant-performancecollector/es_exporter.py -d body -g $2 -s $1 -f $3 -t $4
stats=`echo "bodystats_"$1"_by_"$2"_"$3"_to_"$4`
findfile="find /opt/cloudant-performancecollector/results -name "$stats"* | tail -n 1"
statsfile=`eval $findfile`
#rm -f $statsfile
