#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Usage:
# spdns-client.py <hostname> <user> <passwd>
#
# With xargs and arguments-file:
# xargs -a spdns-client.args -n 3 spdns-client.py
#
# Copyright 2013 -- Michael Nowak 

import re
import urllib

re_ipv4 = re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b")

url_ip = "http://checkip.dyndns.com"
url_update = "http://www.spdns.de/nic/update"

def ip_address():
	response = urllib.urlopen(url_ip)
	body = response.read()
	match = re_ipv4.search(body)
	if match:
		return match.group()
	else:
		return None

def dns_update(hostname, ip, user, passwd):
	params = urllib.urlencode({'hostname': hostname, 'myip': ip, 'user': user, 'pass': passwd})
	response = urllib.urlopen(url_update, params)
	body = response.read()
	code = body.split(' ', 1)[0]
	if code == 'good':
		return True
	elif code == 'nochg':
		ip_current = body.split(' ', 1)[-1]
		if ip == ip_current:
			return True
		else:
			return False
	else:
		return False

def main(argv):
	if len(argv) != 4:
		print ''
		print "\tUSAGE: " + __file__ + ' <hostname> <user> <passwd>'
		print ''
		return None
	hostname = argv[1]
	user = argv[2]
	passwd = argv[3]
	ip = ip_address()
	if hostname and ip and user and passwd:
		return dns_update(hostname, ip, user, passwd)
	else:
		return False

if __name__ == '__main__':
	import sys
	main(sys.argv)
