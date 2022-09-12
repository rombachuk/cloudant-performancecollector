#!/bin/bash
# set -x
now=`date +%s`
source /opt/cloudant-performancecollector/venv/bin/activate
conninfo=`echo "/opt/cloudant-performancecollector/resources/collect/configuration/perfagent_connection.info"`
/opt/cloudant-performancecollector/venv/bin/python3 /opt/cloudant-performancecollector/metricsdb_collect.py -f $1 -x $conninfo
