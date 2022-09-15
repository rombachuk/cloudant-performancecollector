#!/bin/bash
now=`date +%Y%m%d%H%M` 
cp -r /opt/cloudant-performancecollector /opt/cloudant-performancecollector-bkp-$now
rm -rf /opt/cloudant-performancecollector/*.pyc
cp -r ../cloudant-performancecollector/*.py /opt/cloudant-performancecollector/
cp -r ../cloudant-performancecollector/resources/collect/scripts/* /opt/cloudant-performancecollector/resources/collect/scripts/
cp -r ../cloudant-performancecollector/resources/export/postgres/scripts/* /opt/cloudant-performancecollector/resources/export/postgres/scripts/
cp -r ../cloudant-performancecollector/resources/export/dynatrace/scripts/* /opt/cloudant-performancecollector/resources/export/dynatrace/scripts/
echo 'completed'