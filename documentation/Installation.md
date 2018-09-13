# Installing the specialapi

The specialapi is most conveniently installed on the two load balancers of a cloudant local cluster. The existing virtualip mechanism for the cloudant cluster is also used to provide a highly-available service for this specialapi.
  
The install requires several steps: 
  
* installing (python-based) flask webserver on load balancers
* configuring existing load-balancer haproxys to redirect certain requests to flask
* installing the specialapi software (flask-served content)
* configuring the specialapi features

Optionally, the specialapi can be used as a front-end to service api-based requests to a running cloudant-performancecollector. This capability requires the cloudant-performancecollector to be installed and running.

## Load Balancer Install
These instructions are for the case where the _api is run on the load-balancer, including perfagent activities.
###	Loading binary
As user 'root', go to /opt and tar the supplied binary using
    
```  
$ tar xvf cloudant-specialapi.N.tar
```  
or patch using the patch by going to /opt/cloudant-specialapi and tar the supplied binary using  
   
```
$ tar xvf cloudant-specialapi.patch.N.tar  
```

###	Flask Server libraries
As user 'root', install python libraries for the api :  
  
```
$ pip install flask
$ pip install requests  
```  
### 	Configuring haproxy for Flask backend
####	Number of logline fields
The /etc/haproxy/haproxy.cfg is used to define the log format of the haproxy.log file, and the number of fields.  
The number of fields must be synched in the /opt/cloudant-specialapi/perfagent-collect.conf 'base_index' parameter:  

* cookie capture set  
If the haproxy.cfg includes lines for capturing the request header and cookie, such as  
  
```
  capture request header Authorization len 256    
  capture cookie AuthSession= len 256  
```
then set base_index = 19 (default)

* cookie capture not set  
If the haproxy.cfg does not include these captures, then set base_index = 17

####	_api backend
The \_api endpoint backend is configured to point to localhost:5000 when the api is run on a load-balancer.

lines are added after the dashboard setup. They follow a similar pattern to the dashboard setup. 

1)	Add acl for api_assets after dashboard_assets
    
```  
acl dashboard_assets path_beg /dashboard.     
acl api_assets path_beg /_api
```  

2)	Add use\_backend for api\_assets\_host after dashboard\_assets\_host

```  
use_backend dashboard_assets_host if dashboard_assets      
use_backend api_assets_host if api_assets  
```  

3)	Add backend api\_assets\_host after 'backend dashboard\_assets\_host'  

```
backend api_assets_host 
  option httpchk GET /_api    
  server localhost 127.0.0.1:5000 check inter 7s   
```  

Restart the load balancer (cast node restart) after the change to the haproxy.cfg file.
### 	Configuring Connectivity & API Usage
Now configure the API as described in 'add link here'.  

If you are going to use the perfagent on this load-balancer,  configure the perfagent as described in 'add link here'.  
 
Once the API is configured with the necessary information, you need to enable the services so that they run on reboot:  

```
$ cp csapi /etc/init.d
$ cp csapi_migrate /etc/init.d
$ cp csapi_perfagent /etc/init.d
$ systemctl enable csapi
$ systemctl enable csapi_migrate
$ systemctl enable csapi_perfagent 
```
(cspai_perfagent only if the worker is to run on this server).  
  
Then start the services with  
  
```   
$ systemctl start csapi
$ systemctl start csapi_migrate
$ systemctl start csapi_perfagent  
```  
(cspai_perfagent only if the worker is to run on this server) 

The perfagent is cpu-intensive if it is asked to process long time ranges on busy clusters, and will occupy cpu capacity on the load-balancer in these cases.  
Consider running the api on a separate server in these cases.


##	Separate Server Install
###	Loading binary
The following instructions apply to a separate server running Centos7.4 or RHEL7.4
As user 'root' on the separate server, go to /opt and tar the supplied binary using
  
```
$ tar xvf cloudant-specialapi.N.tar
```  
or patch using the patch by going to /opt/cloudant-specialapi and tar the supplied binary using  
  
```
$ tar xvf cloudant-specialapi.patch.N.tar
```  

###	Python libraries
As user 'root', install python libraries for the api :  
  
```  
$ pip install flask
$ pip install pandas
$ pip install requests
```  
### 	Configuring haproxy for api backend
####	Which proxies
Do these steps on each load-balancer that is serving traffic for your cluster.  
Normally this will be on two proxies.  
The haproxy.log files for each load-balancer should be copied via rsyslog to the same apiserver if the perfagent feature is to be used.
####	Number of logline fields
The /etc/haproxy/haproxy.cfg is used to define the log format of the haproxy.log file, and the number of fields.  
The number of fields must be synched in the /opt/cloudant-specialapi/perfagent-collect.conf 'base_index' parameter:  

* cookie capture set  
If the haproxy.cfg includes lines for capturing the request header and cookie, such as  
  
```
  capture request header Authorization len 256    
  capture cookie AuthSession= len 256  
```
then set base_index = 19 (default)

* cookie capture not set  
If the haproxy.cfg does not include these captures, then set base_index = 17



####	_api backend
The \_api endpoint backend is configured to point to localhost:5000 when the api is run on a load-balancer.

lines are added after the dashboard setup. They follow a similar pattern to the dashboard setup. 

1)	Add acl for api_assets after dashboard_assets
    
```  
acl dashboard_assets path_beg /dashboard.     
acl api_assets path_beg /_api
```  

2)	Add use\_backend for api\_assets\_host after dashboard\_assets\_host

```  
use_backend dashboard_assets_host if dashboard_assets      
use_backend api_assets_host if api_assets  
```  

3)	Add backend api\_assets\_host after 'backend dashboard\_assets\_host'  

```
backend api_assets_host 
  option httpchk GET /_api    
  server localhost 127.0.0.1:5000 check inter 7s   
```  

Restart the load balancer (cast node restart) after the change to the haproxy.cfg file.
###	Configuring Connectivity & API Usage
Now, as root on the separate apiserver, configure the API as described in 'add link here'.  
If you are going to use the perfagent on this server. Configure the perfagent as described in 'add link here'   
Once the API is configured with the necessary information, you need to enable the services so that they run on reboot:  

```  
$ cp csapi /etc/init.d
$ cp csapi_migrate /etc/init.d
$ cp csapi_perfagent /etc/init.d
$ systemctl enable csapi
$ systemctl enable csapi_migrate
$ systemctl enable csapi_perfagent
```  
 (csapi\_perfagent only if the worker is to run on this server)  
Then start the services with  
  
``` 
$ systemctl start csapi
$ systemctl start csapi_migrate
$ systemctl start csapi_perfagent
```   
 (if the worker is to run on this server)

The perfagent has  -H -L options to identify the log file to be processed. Use this to distinguish logfiles from different load balancers. See 'add link here'


