#!/usr/bin/env python

#########################################################################
#                                                                       #
# Script for finding neighbor web servers in local network              #
#                                                                       #
# Author: Hugo Duksis <duksis@gmail.com>                                #
# Usage: python neighbor_search.py
# TODO: move pinging in multiple treads to increase performance         #
#                                                                       #
#########################################################################

import httplib, socket, os

ADDRESS_RANGE = range(1,256)
DEFAULT_PORTS = [80                 # Default http
                ,8080               # unofficial http
                ,3000,3001          # default rails 3000 plus some additional
                ,1337               # sinatra 1337
                ,9393]              # shotgun 9393
ACCEPTABLE_RESPONSE_CODES = [200 # Success
                            ,301 # Permanent redirect
                            ,302 # Temporary redirect
                            ,304 # Not modified
                            ,403 # Forbidden
                            ,404]# Page not found

def get_current_ip():
   ip = '127.0.0.1'
   try:
       ip = socket.gethostbyname(socket.gethostname())
   except socket.error, e:
       s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
       s.connect(("8.8.8.8", 80))
       ip = s.getsockname()[0]
       s.close()
   return ip

def ping_ip(ip):
    return os.system('ping -c1 -W1 ' + ip + ' >/dev/null') == 0

def get_neighbor_ips(ip):
    """ Get all neighbor IP's for given IP """
    ips = []
    if ip.count('.') == 3:
        base = ip[0:ip.rfind('.')+1]
        for extension in ADDRESS_RANGE:
            neighbor = base + str(extension)
            # exclude current ip
            if neighbor != ip:
                ips.append(neighbor)
    return ips

def check_address(url, port, timeout=0.1):
    """
      makes a http request to given url:port
      and returns status: True/False and message: 'OK'/'Connection refused'
    """
    h = httplib.HTTPConnection(url, port, timeout=timeout)
    status = False
    try:
        h.request('GET','/')
        r = h.getresponse()
        msg = str(r.reason) + ' ' + str(r.status)
        # OK or Not modified
        if r.status in ACCEPTABLE_RESPONSE_CODES:
          status = True
    except socket.error, e:
        msg = e.strerror
    except:
        msg = 'Unexpected error'
    return status, url + ':' + str(port) + ' ' + str(msg)

def scan_ports(url, ports):
    """ Verify if url is responding to http requests on given ports """
    messages = []
    for port in ports:
        status, message = check_address(url, port)
        if status:
            messages.append(message)
    return messages

def scan(ips=None, ports=DEFAULT_PORTS):
    """ Verify if urls are responding to http requests on given ports """
    if not ips:
        local_ip = get_current_ip()
        ips = get_neighbor_ips(local_ip)
    messages = []
    for ip in ips:
        if ping_ip(ip):
            messages.extend(scan_ports(ip, ports))
    if len(messages) > 0:
        for message in messages:
            print message
    else:
        print 'No neighbors found.'

#-----------------------------------------------------------------------------

if __name__ == '__main__':
    scan()
