#!/bin/bash
# set -x
/opt/cloudant-performancecollector/resources/collect/scripts/bodydata_collect.sh $1 $2 $3 $4 $5 
/opt/cloudant-performancecollector/resources/export/postgres/scripts/onetime/bodydata_load.sh $1 $2 $3 $4 
stats=`echo "bodystats_"$1"_by_"$2"_"$3"_to_"$4`
findfile="find /opt/cloudant-performancecollector/results -name "$stats"* | tail -n 1"
statsfile=`eval $findfile`
rm -f $statsfile
