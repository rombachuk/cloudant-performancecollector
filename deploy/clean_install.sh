#!/bin/bash
now=`date +%Y%m%d%H%M` 
cp -r /opt/cloudant-performancecollector /opt/cloudant-performancecollector-bkp-$now
mkdir /opt/cloudant-performancecollector-bkp-$now/init.d
rm -rf /opt/cloudant-performancecollector
cp -r ../cloudant-performancecollector /opt
python3 -m venv /opt/cloudant-performancecollector/venv
source /opt/cloudant-performancecollector/venv/bin/activate
pip install --upgrade pip
pip3 install requests
pip3 install cython
pip3 install numpy
pip3 install pandas
pip3 install flask
echo 'completed'
