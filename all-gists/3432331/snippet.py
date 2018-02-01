
#!/usr/bin/python
# Use this script to update a DNS override using the webfaction API
# be sure to set your username, password, dns override, and ethenet interface.
# Then add a crontab entry for the script, I use every 5 minutes
# */5 * * * * /path/to/ddns.py
# This is safe as the script exit(0)'s if the ip is the same as wehat is recorded in the file.
# Webfaction documentation on DNS overrides
# http://docs.webfaction.com/user-guide/domains.html#overriding-dns-records-with-the-control-panel

import xmlrpclib

import socket
import fcntl
import struct

web_faction_username = 'your_user_name'
web_faction_password = 'your_password'
web_faction_dns_override = 'your_dns_override'
ethernet_interface = 'your_wan_interface'  # probably eth0 or eth1

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])


try:
    old_ip_address = open('my_ip').read()
    print 'Old IP: %s' % old_ip_address
except:
    old_ip_address = '0.0.0.0'

print 'Old IP: %s' % old_ip_address

current_ip_address = get_ip_address(ethernet_interface)
print 'Current IP: %s' % current_ip_address
if old_ip_address == current_ip_address:
    exit(0)
    
print 'updating to webfaction'

# Create an object to represent our server.
server = xmlrpclib.ServerProxy('https://api.webfaction.com/')
session_id, account = server.login(web_faction_username, web_faction_password)
server.create_dns_override(session_id, web_faction_dns_override, current_ip_address)

open('my_ip', 'w+').write(current_ip_address)
