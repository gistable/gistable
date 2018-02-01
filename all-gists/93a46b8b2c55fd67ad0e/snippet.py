#!/usr/bin/env python
# -*- coding: utf-8 -*-

# DNSPod dynamic DNS bridge for OpenWRT DDNS service
# This script creates a simple HTTP server and updates your DNSPod DDNS record
# on any HTTP GET request received. This allows you to create a customized DDNS
# service for DNSPod with OpenWRT's standard DDNS support.

# Copyright 2015-2016 rlei @ GitHub
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import BaseHTTPServer
import httplib
import json
import time
import urllib
import sys

HOST_NAME = '0.0.0.0'
PORT_NUMBER = 2080

# Provide your own DNSPod API token
DNSPOD_TOKEN = 'REPLACE_WITH_YOUR_OWN_TOKEN'
DOMAIN = 'YOUR_DOMAIN'
SUB_DOMAIN = 'YOUR_SUB_DOMAIN'
RECORD_LINE = '默认'

domain_id = None
record_id = None

def dnspod_request(api_path, more_params):
    conn = httplib.HTTPSConnection("dnsapi.cn")

    params = {'login_token': DNSPOD_TOKEN, 'format': 'json'}
    params.update(more_params)

    conn.request("POST", api_path, urllib.urlencode(params), {"Content-type": "application/x-www-form-urlencoded"})
    return conn.getresponse()

def get_domain_id(domain):
    response = dnspod_request('/Domain.Info', {'domain': domain})
    result = json.loads(response.read())
    return result['domain']['id']

def get_sub_domain_id(domain_id, sub_domain):
    response = dnspod_request('/Record.List', {'domain_id': domain_id})
    # TODO: handle number of sub domains > 20
    result = json.loads(response.read())
    #print result
    match = [rec for rec in result['records'] if rec['name'] == sub_domain]
    return match[0]['id'] if match else None 

def update_dyndns_record(domain_id, record_id, record_line, sub_domain):
    params = {'domain_id': domain_id,
        'record_id': record_id,
        'record_line': record_line,
        'sub_domain': sub_domain,
        #'value':'your.own.ip.addr'
        }
    return dnspod_request('/Record.Ddns', params)
    
class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(s):
        response = update_dyndns_record(domain_id, record_id, RECORD_LINE, SUB_DOMAIN)
	res_body = response.read()
	print 'DNSPod response: status %d, %s' % (response.status, res_body)

        s.send_response(response.status)
        s.send_header("Content-type", response.getheader("Content-Type", "application/json"))
        s.end_headers()

        s.wfile.write(res_body)

if __name__ == '__main__':
    domain_id = get_domain_id(DOMAIN)
    record_id = get_sub_domain_id(domain_id, SUB_DOMAIN)
    if not record_id:
        print "Can't find record for sub domain " + SUB_DOMAIN
        sys.exit(1)

    print 'DNSPod token: {0}\nDomain: "{1}" id {2}\nSub domain: "{3}.{1}" id {4}\n'.format(DNSPOD_TOKEN, DOMAIN, domain_id, SUB_DOMAIN, record_id)

    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
