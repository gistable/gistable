#!/bin/python

import json, sys, requests, string, random

auth_endpoints = {
    "US": "https://identity.api.rackspacecloud.com/v2.0",
    "UK": "https://lon.identity.api.rackspacecloud.com/v2.0"
}

username = "XXXX"
apikey = "XXXX"

def auth(region, username, password='', apikey=''):
    headers = {
        "Content-Type":"application/json",
        "Accept":"application/json"
    }
    
    path = "/tokens"
    url = "%s%s" %(auth_endpoints[region], path)
    
    if(len(password)) > 0:
        data = {"auth": {"passwordCredentials": {"username": username, "password": password}}}
    elif(len(apikey)) > 0:
        data = {"auth": {"RAX-KSKEY:apiKeyCredentials": {"username": username, "apiKey": apikey}}}
    else:
        return False
        
    data = json.dumps(data)
    r = requests.post(url,data=data,headers=headers, verify=False)
    return r.json()

    
def set_cors(token, url):
    headers = {
        "X-Auth-Token":token,
        "X-Container-Meta-Access-Control-Allow-Origin":url,
        "X-Container-Meta-Access-Control-Max-Age":360
    }
    
    url = "https://storage101.ord1.clouddrive.com/v1/PATH_FOR_YOU/CONTAINER_NAME"
    
    r = requests.post(url,headers=headers, verify=False)
    return r

def print_requests_summary(r):
    print "Status Code: ",r.status_code
    print "Output (text): ",r.text
    print "Output (json): ",r.json

auth_data = auth("US",username,apikey=apikey)
retval = set_cors(auth_data["access"]["token"]["id"],'http://localhost')
print_requests_summary(retval)
