#!/bin/env python

import sys
import requests
import re

# To use this script with openssh-server 6.2 or newer
# Add these lines to /etc/ssh/sshd_config
#
# AuthorizedKeysCommand /path/to/get_github_pubkey.py
# AuthorizedKeysCommandUser nobody

# Example account with no keys : telliott
# Example nonexistent account : thisaccountdoesntexist
# Example accountname that is too long : 1234567890123456789012345678901234567890

# To prep the user merely create him or her and add them to the user_map
#
# useradd jdoe
# useradd asmith -G wheel

# "unix username": "github username"
user_map = {"jdoe": "johnd",
            "asmith": "alicesmith"}

github_username_regex = r"^[^-][0-9a-zA-Z-]{0,38}$"
if len(sys.argv) != 2:
    # Username wasn't passed
    exit(1)
if sys.argv[1] not in user_map.keys():
    # User is not allowed
    exit(1)
else:
    github_username = user_map[sys.argv[1]]

if not re.match(github_username_regex, github_username):
    # Github username is invalid
    exit(1)

# Currently this call violates SELinux policy preventing sshd
# from initiating TCP connections. I had to set SELinux to
# permissive to get it to work
r = requests.get('https://github.com/%s.keys' % github_username)

if r.status_code != 200:
    # User doesn't exist
    exit(1)
if len(r.text) == 0:
    # User has no keys loaded
    exit(1)
print(r.text)
