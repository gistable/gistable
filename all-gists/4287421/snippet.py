#!/usr/bin/python

import os
import sys
import urllib

# Change this to match your mail server's REVERSE static IP address
staticIPAddress = "1.0.0.127"

# Change this to an email address you don't mind sending to and from for the notice alert delivery
toFromMailAddress = "somebody@example.com"

### Spamhaus blocks IP addresses using DNSBL that is all distributed via standard DNS records.
### e.g. if you lookup a reverse-ip prepended blacklist URL:
###
### > dig -t a 1.0.0.127.zen.spamhaus.org
###
### You'll only get a found record if the IP address (127.0.0.1) IS in one of Spamhaus's blacklists.
### 
### I'm using "dig" on my system to script this, but you might consider using a DNS library for python or another method.

# Lookup the pertinent DNS query to determine if the specified IP address is listed. Technically 
# we should be looking up the A record first, but in my tests the TXT record will contain the URL
# for the pertinent blacklist information only when the IP address is in fact listed on some 
# blacklists.

dnsHostname = staticIPAddress + ".zen.spamhaus.org"
p = os.popen("dig +short -t TXT " + dnsHostname)
lookupResult= p.read()

# If the IP address is not listed in any Spamhaus lists, the string is empty!
notListed = (len(lookupResult) == 0)

if (notListed is False):
        msg = """To: %s
From: %s
Subject: Spamhaus spam list addition alert

The IP address %s has unfortunately been added to one of the lists maintained by the Spamhaus project.

For more information, visit the pertinent Spamhaus info URL: %s""" % (toFromMailAddress, toFromMailAddress, staticIPAddress, lookupResult)
        SENDMAIL = "/usr/sbin/sendmail" # sendmail location
        p = os.popen("%s -t -i" % SENDMAIL, "w")
        p.write(msg);
        p.close()

        print msg
