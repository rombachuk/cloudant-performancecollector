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
escacertf=`echo $escacert | sed -e 's/\s/\\\n/g' |sed -e 's/BEGIN\\\nCERT/BEGIN CERT/g' | sed -e 's/END\\\nCERT/END CERT/g'`
#esconn='"url":"'$esurl'","basicAuthUser":"'$esuser'","basicAuthPassword":"'$espass'"'
esconn='"url":"'$esurl'","basicAuthUser":"'$esuser'","basicAuthPassword":"'$espass'","secureJsonData":{"tlsCACert":"'$escacertf'"}'
else
esconn='"url":"'$esurl'","basicAuthUser":"'$esuser'","basicAuthPassword":"'$espass'"'
fi
others=`cat others.json`
others1s=`cat others1s.json`
echo -e "Installing grafana datasources"
json1='{"name":"couchdbstats_bodyminute","database":"couchdbstats_body_minute*",'$esconn','$others'}'
json2='{"name":"couchdbstats_bodysecond","database":"couchdbstats_body_second*",'$esconn','$others1s'}'
json3='{"name":"couchdbstats_clientverb","database":"couchdbstats_client_verb*",'$esconn','$others'}'
json4='{"name":"couchdbstats_proxyverb","database":"couchdbstats_proxy_verb*",'$esconn','$others'}'
json5='{"name":"couchdbstats_proxyendpoint","database":"couchdbstats_proxy_endpoint*",'$esconn','$others'}'
json6='{"name":"couchdbstats_couchdbnodehost","database":"couchdbstats_couchdbnode_host*",'$esconn','$others'}'
json7='{"name":"couchdbstats_couchdbnodeioqtype","database":"couchdbstats_couchdbnode_ioqtype*",'$esconn','$others'}'
json8='{"name":"couchdbstats_couchdbnodesmoosh","database":"couchdbstats_couchdbnode_smoosh*",'$esconn','$others'}'
json9='{"name":"couchdbstats_couchdbvolumedb","database":"couchdbstats_couchdbvolume_db*",'$esconn','$others'}'
json10='{"name":"couchdbstats_couchdbvolumeview","database":"couchdbstats_couchdbvolume_view*",'$esconn','$others'}'
curlcmd="/usr/bin/curl -k --connect-timeout 60  -s -u "$gruser":"$grpass" -X POST "$grurl"/api/datasources -H 'Content-Type:application/json' -d '$json1'"
eval $curlcmd
curlcmd="/usr/bin/curl -k --connect-timeout 60  -s -u "$gruser":"$grpass" -X POST "$grurl"/api/datasources -H 'Content-Type:application/json' -d '$json2'"
eval $curlcmd
curlcmd="/usr/bin/curl -k --connect-timeout 60  -s -u "$gruser":"$grpass" -X POST "$grurl"/api/datasources -H 'Content-Type:application/json' -d '$json3'"
eval $curlcmd
curlcmd="/usr/bin/curl -k --connect-timeout 60  -s -u "$gruser":"$grpass" -X POST "$grurl"/api/datasources -H 'Content-Type:application/json' -d '$json4'"
eval $curlcmd
curlcmd="/usr/bin/curl -k --connect-timeout 60  -s -u "$gruser":"$grpass" -X POST "$grurl"/api/datasources -H 'Content-Type:application/json' -d '$json5'"
eval $curlcmd
curlcmd="/usr/bin/curl -k --connect-timeout 60  -s -u "$gruser":"$grpass" -X POST "$grurl"/api/datasources -H 'Content-Type:application/json' -d '$json6'"
eval $curlcmd
curlcmd="/usr/bin/curl -k --connect-timeout 60  -s -u "$gruser":"$grpass" -X POST "$grurl"/api/datasources -H 'Content-Type:application/json' -d '$json7'"
eval $curlcmd
curlcmd="/usr/bin/curl -k --connect-timeout 60  -s -u "$gruser":"$grpass" -X POST "$grurl"/api/datasources -H 'Content-Type:application/json' -d '$json8'"
eval $curlcmd
curlcmd="/usr/bin/curl -k --connect-timeout 60  -s -u "$gruser":"$grpass" -X POST "$grurl"/api/datasources -H 'Content-Type:application/json' -d '$json9'"
eval $curlcmd
curlcmd="/usr/bin/curl -k --connect-timeout 60  -s -u "$gruser":"$grpass" -X POST "$grurl"/api/datasources -H 'Content-Type:application/json' -d '$json10'"
eval $curlcmd
curlcmd="/usr/bin/curl -k --connect-timeout 60  -s -u "$gruser":"$grpass" -X POST "$grurl"/api/datasources -H 'Content-Type:application/json' -d '$json11'"
eval $curlcmd