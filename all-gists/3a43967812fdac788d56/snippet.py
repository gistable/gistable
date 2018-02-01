#!/usr/bin/env python


# Takes hosts file and converts to DNSCrypt blacklist-domains file
# so you could block malicious hosts on DNSCrypt
# (when alternating to DNSCrypt instead of dnsmasq in my scenario)
# hosts file from https://github.com/StevenBlack/hosts
# See https://dnscrypt.org/ IP/domain names blocking

import re
import os

badguys_pattern = re.compile(
    '^0.0.0.0(\s*|\t*)(.*)\n|^127.0.0.1(\s*|\t*)(.*)\n')
localhost_pattern = re.compile(
    '^0.0.0.0.*localhost\.localdomain.*$|^(?!\#)(.*)localhost.*$|^(?!\#).*broadcasthost.*$|^0.0.0.0.*local.*$')
comment_pattern = re.compile('#(.*)\n')

os.unlink("blacklist-domains")
# touch blacklist-domains first if it doesn't exist
output = open("blacklist-domains", "w")

with open('hosts.txt', 'r') as f:
    for line in f.readlines():
        if re.match(localhost_pattern, line):
            pass
        elif re.match(comment_pattern, line):
            pass
        else:
            m = badguys_pattern.match(line)
            if m:
                if m.group(2) is not None:
                    output.write(m.group(2) + "\n")

output.close()

# if using DNSCrypt-OSXClient on Mac
# mv blacklist-ips /Library/Application\ Support/DNSCrypt/control/

