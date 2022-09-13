##!/bin/bash 
# set -x
nowepoch=`date +%s`
let oldepoch=$nowepoch-$1*60-1200
let fromepoch=$nowepoch-$1*60
let toepoch=$nowepoch-$2*60
today=`date -d @$fromepoch +%Y%m%d`
oldpretty=`date -d @$oldepoch +%Y%m%d%H%M`
frompretty=`date -d @$fromepoch +%Y%m%d%H%M`
topretty=`date -d @$toepoch +%Y%m%d%H%M`
fromgrep=`date -d @$fromepoch +%d/%b/%Y:%H:%M`
oldlogfile=`echo "/opt/cloudant-performancecollector/tmp/"finaltail$HOSTNAME"_"$oldpretty"_haproxy.log.gz"`
tmplogfile=`echo "/opt/cloudant-performancecollector/tmp/"tail$HOSTNAME"_"$frompretty"_haproxy.log.gz"`
finallogfile=`echo "/opt/cloudant-performancecollector/tmp/"finaltail$HOSTNAME"_"$frompretty"_haproxy.log.gz"`
rm -f $oldlogfile
tail -n 500000 /var/log/haproxy.log | grep $fromgrep | gzip > $tmplogfile
mv $tmplogfile $finallogfile