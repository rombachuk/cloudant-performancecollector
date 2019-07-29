#!/bin/bash
url=`/usr/bin/grep 'url' /opt/cloudant-performancecollector/resources/export/elasticsearch/configuration/perfagent_es_connection.info | sed 's/\s\s*/ /g' | cut -d' ' -f2`
credentials=`/usr/bin/grep 'credentials' /opt/cloudant-performancecollector/resources/export/elasticsearch/configuration/perfagent_es_connection.info | sed 's/\s\s*/ /g' | cut -d' ' -f2`
esuser=`/usr/bin/echo $credentials | /usr/bin/base64 --decode | cut -d ":" -f 1`
espass=`/usr/bin/echo $credentials | /usr/bin/base64 --decode | cut -d ":" -f 2`
cd /opt/cloudant-performancecollector/resources/export/elasticsearch/schema
echo -e "Installing elasticsearch templates (overrides current values - may take several minutes - please wait for Installation completed message)"
echo -e "Installing body_minute template"
/usr/bin/curl -k --connect-timeout 60 -m 180 -u $esuser:$espass -X PUT $url/_template/body_minute_template -H 'Content-Type:application/json' -d @body_minute_template.json
echo -e "\nInstalling body_second template"
/usr/bin/curl -k --connect-timeout 60 -m 180 -u $esuser:$espass -X PUT $url/_template/body_second_template -H 'Content-Type:application/json' -d @body_second_template.json
echo -e "\nInstalling client_verb template"
/usr/bin/curl -k --connect-timeout 60 -m 180 -u $esuser:$espass -X PUT $url/_template/client_verb_template -H 'Content-Type:application/json' -d @client_verb_template.json
echo -e "\nInstalling couchdbnode_host template"
/usr/bin/curl -k --connect-timeout 60 -m 180 -u $esuser:$espass -X PUT $url/_template/couchdbnode_host_template -H 'Content-Type:application/json' -d @couchdbnode_host_template.json
echo -e "\nInstalling couchdnode_ioqtype template"
/usr/bin/curl -k --connect-timeout 60 -m 180 -u $esuser:$espass -X PUT $url/_template/couchdbnode_ioqtype_template -H 'Content-Type:application/json' -d @couchdbnode_ioqtype_template.json
echo -e "\nInstalling couchdbnode_smoosh template"
/usr/bin/curl -k --connect-timeout 60 -m 180 -u $esuser:$espass -X PUT $url/_template/couchdbnode_smoosh_template -H 'Content-Type:application/json' -d @couchdbnode_smoosh_template.json
echo -e "\nInstalling couchdbvolume_db template"
/usr/bin/curl -k --connect-timeout 60 -m 180 -u $esuser:$espass -X PUT $url/_template/couchdbvolume_db_template -H 'Content-Type:application/json' -d @couchdbvolume_db_template.json
echo -e "\nInstalling couchdbvolume_view template"
/usr/bin/curl -k --connect-timeout 60 -m 180 -u $esuser:$espass -X PUT $url/_template/couchdbvolume_view_template -H 'Content-Type:application/json' -d @couchdbvolume_view_template.json
echo -e "\nInstalling proxy_verb template"
/usr/bin/curl -k --connect-timeout 60 -m 180 -u $esuser:$espass -X PUT $url/_template/proxy_verb_template -H 'Content-Type:application/json' -d @proxy_verb_template.json
echo -e "\nInstalling proxy_endpoint template"
/usr/bin/curl -k --connect-timeout 60 -m 180 -u $esuser:$espass -X PUT $url/_template/proxy_endpoint_template -H 'Content-Type:application/json' -d @proxy_endpoint_template.json
echo -e "\nInstallation of templates completed"
cd -
