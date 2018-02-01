#!/usr/bin/env python

# DESCRIPTION:
#
#   This script is meant to be run as a root cronjob.  You can run it however frequently
#   you desire - I run it every minute.  It determines the number of streams, and cross
#   references the usernames.  If there are duplicate usernames, it checks if the IP 
#   addresses are different.  If so, it generates IPTables rules that will drop packets 
#   from both IP addresses.  
#
#   This does not save any IPTables rules, so on a reboot or service restart the rules 
#   will be lost. 

import urllib2
import os
from xml.etree import ElementTree as etree

# NOTE: This will only work from the Plex server itself (executing iptables rules locally)
# Plex Server details
server_address = ""
server_port = ""
excluded_users = []
http_response = urllib2.urlopen("http://" + server_address + ":" + server_port + "/status/sessions")
xml_response = http_response.read()
http_response.close()

stream_root = etree.fromstring(xml_response)
current_streams = stream_root.findall('Video')

user_ip_dict = {}

for stream in current_streams:
    username = stream.findall('User')[0].attrib['title']
    ip_address = stream.findall('Player')[0].attrib['address']

    if username in user_ip_dict and user_ip_dict[username] != ip_address:
        # Generate rules
        iptables_first_rule = "INPUT -p tcp -s " + ip_address + " --dport " + server_port + " -j DROP"
        iptables_second_rule = "INPUT -p tcp -s " + user_ip_dict[username] + " --dport " + server_port + " -j DROP"

        # Delete rules first if they exists (prevents dupes)
        os.system("iptables -D " + iptables_first_rule)
        os.system("iptables -D " + iptables_second_rule)

        # Ban IP's
        os.system("iptables -I " + iptables_first_rule)
        os.system("iptables -I " + iptables_second_rule)
    elif username not in excluded_users:
        # Add to stream_dict
        user_ip_dict[username] = ip_address
