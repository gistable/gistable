#This is a little example of how to make a PUT request (see  http://microformats.org/wiki/rest/urls )
#To a API written with tastypie (https://github.com/toastdriven/django-tastypie )

# import the standard JSON parser
import json
# import the REST library (from http://code.google.com/p/python-rest-client/)
from restful_lib import Connection

#site url 
base_url = "http://IP/api/v1"
conn = Connection(base_url)

#get the global config dict
globalconfig = conn.request_get('/globalconfig/')
globalconfig = json.loads(globalconfig["body"])
globalconfig = globalconfig["objects"][0]

#set the args
globalconfig["sfftrim"] = True

#make the put REST request to update the resource
result = conn.request_put('/globalconfig/1/', body=json.dumps(globalconfig), headers={'content-type':'application/json'})