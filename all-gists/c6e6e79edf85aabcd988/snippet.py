#!/usr/bin/python

import urllib, xml.etree.ElementTree as et

ns = { "pingdom" : "http://www.pingdom.com/ns/PingdomRSSNamespace" }

rss = et.fromstring(urllib.urlopen("https://www.pingdom.com/rss/probe_servers.xml").read())

for ip in rss.iterfind("channel/item/pingdom:ip", namespaces = ns):
  print ip.text
