#!/bin/bash
cd /opt/cloudant-performancecollector/resources/export/elasticsearch/grafana
grurl=`/usr/bin/grep 'url' /opt/cloudant-performancecollector/resources/export/elasticsearch/grafana/grafana_connection.info | sed 's/\s\s*/ /g' | cut -d' ' -f2`
grcredentials=`/usr/bin/grep 'credentials' /opt/cloudant-performancecollector/resources/export/elasticsearch/grafana/grafana_connection.info | sed 's/\s\s*/ /g' | cut -d' ' -f2`
grcredentials=`/usr/bin/grep 'credentials' /opt/cloudant-performancecollector/resources/export/elasticsearch/grafana/grafana_connection.info | sed 's/\s\s*/ /g' | cut -d' ' -f2`
gruser=`/usr/bin/echo $grcredentials | /usr/bin/base64 --decode | cut -d ":" -f 1`
grpass=`/usr/bin/echo $grcredentials | /usr/bin/base64 --decode | cut -d ":" -f 2`
esurl=`/usr/bin/grep 'url' /opt/cloudant-performancecollector/resources/export/elasticsearch/configuration/perfagent_es_connection.info | sed 's/\s\s*/ /g' | cut -d' ' -f2`
escredentials=`/usr/bin/grep 'credentials' /opt/cloudant-performancecollector/resources/export/elasticsearch/configuration/perfagent_es_connection.info | sed 's/\s\s*/ /g' | cut -d' ' -f2`
esuser=`/usr/bin/echo $escredentials | /usr/bin/base64 --decode | cut -d ":" -f 1`
espass=`/usr/bin/echo $escredentials | /usr/bin/base64 --decode | cut -d ":" -f 2`
estls=`/usr/bin/grep 'ssl' /opt/cloudant-performancecollector/resources/export/elasticsearch/configuration/perfagent_es_connection.info | sed 's/\s\s*/ /g' | cut -d' ' -f2`
escertfile=`/usr/bin/grep 'certificate' /opt/cloudant-performancecollector/resources/export/elasticsearch/configuration/perfagent_es_connection.info | sed 's/\s\s*/ /g' | cut -d' ' -f2`
if [ $estls == "enabled" ]
then
escacert=`/usr/bin/cat $escertfile`
esconn='"url":"'$esurl'","basicAuthUser":"'$esuser'","basicAuthPassword":"'$espass'"'
#esconn='"url":"'$esurl'","basicAuthUser":"'$esuser'","basicAuthPassword":"'$espass'","secureJsonData":{"tlsCACert":"'$escacert'"}'
else
esconn='"url":"'$esurl'","basicAuthUser":"'$esuser'","basicAuthPassword":"'$espass'"'
fi
others=`cat others.json`
echo -e "Installing grafana datasources"
json1='{"name":"couchdbstats-es-couchdbnodehost","database":"couchdbnode_host*",'$esconn','$others'}'
json2='{"name":"couchdbstats-es-couchdbnodeioqtype","database":"couchdbnode_ioqtype*",'$esconn','$others'}'
json3='{"name":"couchdbstats-es-couchdbnodesmoosh","database":"couchdbnode_smoosh*",'$esconn','$others'}'
curlcmd="/usr/bin/curl -k --connect-timeout 60  -s -u "$gruser":"$grpass" -X POST "$grurl"/api/datasources -H 'Content-Type:application/json' -d '$json1'"
eval $curlcmd
curlcmd="/usr/bin/curl -k --connect-timeout 60  -s -u "$gruser":"$grpass" -X POST "$grurl"/api/datasources -H 'Content-Type:application/json' -d '$json2'"
eval $curlcmd
curlcmd="/usr/bin/curl -k --connect-timeout 60  -s -u "$gruser":"$grpass" -X POST "$grurl"/api/datasources -H 'Content-Type:application/json' -d '$json3'"
eval $curlcmd
