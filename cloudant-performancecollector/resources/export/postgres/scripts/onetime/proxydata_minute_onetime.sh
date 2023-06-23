#!/bin/bash
# set -x
start=$2
startus="${start:4:2}/${start:6:2}/${start:0:4} ${start:8:2}:${start:10:2}:00"
startepoch=`date -d "$startus" +"%s"`
end=$3
endus="${end:4:2}/${end:6:2}/${end:0:4} ${end:8:2}:${end:10:2}:00"
endepoch=`date -d "$endus" +"%s"`
let fromepoch=$startepoch
let toepoch=$fromepoch+1800
while [[ $toepoch -lt $endepoch ]]; do
from=`date -d@$fromepoch +"%Y%m%d%H%M"`
to=`date -d@$toepoch +"%Y%m%d%H%M"`
echo $from
echo $to
/opt/cloudant-performancecollector/resources/collect/scripts/proxydata_minute_collect.sh $1 $from $to $4
/opt/cloudant-performancecollector/resources/export/postgres/scripts/onetime/proxydata_minute_load.sh $1 $from $to
let fromepoch=$toepoch
let toepoch=$fromepoch+1800
done
if [[ $fromepoch -lt $endepoch ]]; then
from=`date -d@$fromepoch +"%Y%m%d%H%M"`
to=`date -d@$endepoch +"%Y%m%d%H%M"`
echo $from
echo $to
/opt/cloudant-performancecollector/resources/collect/scripts/proxydata_minute_collect.sh $1 $from $to $4
/opt/cloudant-performancecollector/resources/export/postgres/scripts/onetime/proxydata_minute_load.sh $1 $from $to
fi
