#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: p0we7
# Email : i@iu.vc

def handle_import_error():
    print '\n' + "Import Error:"
    print 'Please install the required 3rd-party modules ' + '\033[4;95m' + 'requests' + '\033[0m' + '\n'
    import sys
    sys.exit()

try:
    import requests
except ImportError:
    handle_import_error()
import json, time, hashlib, re, syslog
import socket, fcntl, struct
from time import gmtime

method = "web"              # web or iface , but interface only support for unix-like
interface = "pppoe0"        # if method set iface , then set interface name
# log = "/var/log/messages" # log file

api_key = "API_KEY"
api_secret = "API_SECRET"
DOMAIN = "YOUR_DOMAIN"      # sample: p0we7.github.com


def getIpAddress(method, ifname="lo"):
    if method == "iface":
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )[20:24])
    if method == "web":
        sock = socket.create_connection(('ip.iu.vc', 6666))
        ip = sock.recv(16)
        sock.close()
        return ip


class XNS(object):
    """docstring for XNS"""

    def __init__(self):
        super(XNS, self).__init__()


    def domainSplit(self, location):
        if location == "pre":
            return re.search('^[a-zA-Z0-9][-a-zA-Z0-9]{0,62}', DOMAIN).group()
        if location == "suf":
            return re.search('(?<=\.)([a-zA-Z0-9][-a-zA-Z0-9]{0,62})\.([a-zA-Z0-9][-a-zA-Z0-9]{0,62})+', DOMAIN).group()


    def headers(self, method, url, data=None):
        request_time = time.strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime())

        if method == "GET":
            hmac = hashlib.md5(api_key + url + request_time + api_secret).hexdigest()
        if method == "PUT":
            hmac = hashlib.md5(api_key + url + str(json.dumps(data)) + request_time + api_secret).hexdigest()
        headers = {
        'API-KEY': api_key,
        'API-REQUEST-DATE': request_time,
        'API-HMAC': hmac,
        'API-FORMAT': 'json'
        }
        return headers


    def getDomainId(self):
        # print self.headers("GET")
        url = api_url + "domain"
        r = requests.get(url, headers=self.headers("GET", url))
        domain = r.json()
        for data in domain['data']:
            if self.domainSplit("suf") in data['domain']:
                return data['id']


    def getRecordId(self):
        url = api_url + "record/" + self.getDomainId()
        r = requests.get(url, headers=self.headers("GET", url))
        domain = r.json()
        for data in domain['data']:
            if self.domainSplit("pre") in data['host']:
                return data['record_id']


    def putRecord(self):
        url = api_url + "record/" + self.getRecordId()

        request_data = {
            "domain_id": self.getDomainId(),
            "host": self.domainSplit("pre"),
            "value": getIpAddress(method, interface),
            "type": "A",
            "ttl": 600,
            "line_id": 1
        }

        r = requests.put(url, data=json.dumps(request_data), headers=self.headers("PUT", url, request_data))
        return r.json()



if __name__ == '__main__':
    requests.packages.urllib3.disable_warnings()   # ignore urlib3 warnings
    api_url = "https://www.cloudxns.net/api2/"

    d = XNS()
    result = d.putRecord()
    syslog.openlog("xnsCloud", syslog.LOG_PID)
    response = result
    response_data = response[u'data']
    syslog.syslog("Update_Status : " + response[u'message'])
    syslog.syslog("Update_IP : " + response_data[u'value'])
    syslog.syslog("Domain_name : " + response_data[u'domain_name'])