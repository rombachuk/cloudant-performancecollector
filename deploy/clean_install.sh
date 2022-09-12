#!/bin/bash
now=`date +%Y%m%d%H%M` 
systemctl stop cpc_api_processor
cp -r /opt/cloudant-performancecollector /opt/cloudant-performancecollector-bkp-$now
mkdir /opt/cloudant-performancecollector-bkp-$now/init.d
cp /etc/init.d/cpc_api_processor /opt/cloudant-performancecollector-bkp-$now/init.d
rm -rf /opt/cloudant-performancecollector
rm -f /etc/init.d/cpc_api_processor
cp -r ../cloudant-performancecollector /opt
python3 -m venv /opt/cloudant-performancecollector/venv
source /opt/cloudant-performancecollector/venv/bin/activate
pip3 install requests
pip3 install cython
pip3 install numpy
pip3 install pandas
pip3 install flask
echo 'completed'
