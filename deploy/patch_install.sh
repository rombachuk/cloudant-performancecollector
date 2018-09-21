#!/bin/bash
now=`date +%Y%m%d%H%M`
systemctl stop cpc_api_processor
cp -r /opt/cloudant-performancecollector /opt/cloudant-performancecollector-bkp-$now
mkdir /opt/cloudant-performancecollector-bkp-$now/init.d
cp /etc/init.d/cpc_api_processor /opt/cloudant-performancecollector-bkp-$now/init.d
cp -r ../cloudant-performancecollector/*.py /opt/cloudant-performancecollector
cp /opt/cloudant-performancecollector/cpc_api_processor /etc/init.d
systemctl enable cpc_api_processor
systemctl start cpc_api_processor