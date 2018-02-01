#!/bin/env python

##
# Send an alert from Splunk to the pushover.net service. 
#
# You must first sign up for an account with pushover.net and register
# this script as an application. Then ensure that the token and user variables
# are configured below.
##
import os
import requests

apiurl = 'https://api.pushover.net/1/messages.json'                                       
token = '<put your app token here>'
user = '<put your user token here>'

title = os.environ.get('SPLUNK_ARG_4', 'undefined')
events = os.environ.get('SPLUNK_ARG_1', 'undefined')
message = '%s events were returned' % (events)
url = os.environ.get('SPLUNK_ARG_6', 'undefined')

# Format the message ready to be sent
title = title.replace(' ', '+')
message = message.replace(' ', '+')
data = 'token=%s&user=%s&url=%s&title=%s&message=%s' % (token, user, url, title, message)

# Send the message
requests.post(apiurl, data=data)