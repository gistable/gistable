#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import urllib2, re

def ParseIEEEOui(url = "http://standards.ieee.org/develop/regauth/oui/oui.txt"):
  req = urllib2.Request(url)
	res = urllib2.urlopen(req)
	data = res.read()
	IEEOUI = []
	for line in data.split('\n'):
		try:
			mac, company = re.search(r'([0-9A-F]{2}-[0-9A-F]{2}-[0-9A-F]{2})\s+\(hex\)\s+(.+)', line).groups()
			IEEOUI.append(dict(mac=mac, company=company))
		except AttributeError:
			continue
	
	return IEEOUI
