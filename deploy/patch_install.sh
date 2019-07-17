#!/bin/bash
now=`date +%Y%m%d%H%M` 
systemctl stop cbcon
cp -r /opt/cloudant-businesscontinuity /opt/cloudant-businesscontinuity-bkp-$now
mkdir /opt/cloudant-businesscontinuity-bkp-$now/init.d
cp /etc/init.d/cbcon /opt/cloudant-businesscontinuity-bkp-$now/init.d
rm -f /etc/init.d/cbcon
rm -rf /opt/cloudant-businesscontinuity/*.pyc
cp -r ../cloudant-businesscontinuity/*.py /opt/cloudant-businesscontinuity/
cp /opt/cloudant-businesscontinuity/cbcon /etc/init.d
systemctl enable cbcon
systemctl start cbcon

echo 'completed'