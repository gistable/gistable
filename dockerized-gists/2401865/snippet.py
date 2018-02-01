#!/usr/bin/python

# Set up a new A record in Cloudflare, add the details of it along with your account details below
# Make sure this script runs on startup (or whenever you get a new IP...)
#
# @author Aaron Rice <aaron@duedil.com>


import urllib
import json
import sys

try:
  new_ip = urllib.urlopen("http://my-ip.heroku.com/").read()
except:
  print "Error getting IP"
  sys.exit()

# Put your Cloudflare settings here.
# The host must be an A record that already exists in cloudflare
data = {
  "a"     : "DIUP",
  "tkn"   : "API_TOKEN_HERE",
  "u"     : "CLOUDFLARE_EMAIL_HERE",
  "ip"    : new_ip.strip(),
  "z"     : "DOMAIN_HERE",
  "hosts" : "DNSNAME.DOMAIN_HERE",
}

try:
  dns_response = json.loads(urllib.urlopen("https://www.cloudflare.com/api_json.html", urllib.urlencode(data)).read())
  if dns_response[u'result'] == "success":
    print "IP updated to " + new_ip,
  else:
    print "Error Setting IP"
except:
  print "Error with cloudflare API"