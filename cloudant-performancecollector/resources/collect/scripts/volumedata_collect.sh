#!/bin/bash
# set -x
now=`date +%s`
conninfo=`echo "/opt/cloudant-performancecollector/resources/collect/configuration/perfagent_connection.info"`
/usr/bin/python /opt/cloudant-performancecollector/volume_collect.py -x $conninfo