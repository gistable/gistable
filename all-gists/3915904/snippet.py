#!/usr/bin/python
# Send SMS with current IP address via Twilio
# Copyright 2012, Kenley Cheung
# Dual licensed under the MIT or GPL Version 2 licenses.
from twilio.rest import TwilioRestClient
import httplib

# Configuration
account = "ACXXXXXXXXXXXXXXXXX"
token = "ZZZZZZZZZZZZZZZZZZZZZ"
destination_number = "+17185550000"
source_number = "+15185550000"

# Constants
ipv4_test = "ipv4.icanhazip.com"
ipv6_test = "ipv6.icanhazip.com"

client = TwilioRestClient(account, token)
ipv4_address = None
ipv6_address = None

# Get IPv4 address.
try:
    ipv4_connection = httplib.HTTPConnection(ipv4_test)
    ipv4_connection.request("GET", "/")
except httplib.NotConnected:
    print "No internet connection."
    sys.exit(1)
except:
    sys.exit(2)
else:
    ipv4_response = ipv4_connection.getresponse()
    ipv4_address = ipv4_response.read()
    ipv4_connection.close()
    print "Public IPv4 address is " + ipv4_address
    client.sms.messages.create(to=destination_number, from_=source_number, body="IPv4: " + ipv4_address)

# Get IPv6 address
try:
    ipv6_connection = httplib.HTTPConnection(ipv6_test)
    ipv6_connection.request("GET", "/")
except:
    print "No IPv6 address."
else:
    ipv6_response = ipv6_connection.getresponse()
    ipv6_address = ipv6_response.read()
    ipv6_connection.close()
    print "Public IPv6 address is " + ipv6_address
    client.sms.messages.create(to=destination_number, from_=source_number, body="IPv6: " + ipv6_address)
