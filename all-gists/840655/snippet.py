"""
usage:

    fab -f distkeys.py set_hosts:/path/to/hosts_file add_key:/path/to/key

    Use --password and --user options as necessary

Inspired by shell script at http://github.com/mlbright/mybin/raw/master/distkeys.sh
Fabric recipe to distribute your ssh key to large number of hosts.

Thanks to Jeff Forcier for clearing up the env.hosts setup.
"""

import sys
import os
from fabric.api import env, run

SSH_HOME  = "~/.ssh"
AUTH_KEYS = "~/.ssh/authorized_keys"
PUB_KEY   = "~/.ssh/id_rsa.pub"
HOSTS_FILE = "~/.hosts"

def _get_public_key(key_file):

    with open(os.path.expanduser(key_file)) as fd:
        key = fd.readline().strip()
    return key

# ---------------------------------------------------------------------------- #

def set_hosts(filename=HOSTS_FILE):

    with open(os.path.expanduser(filename)) as fd:
        env.hosts = [ host.strip() for host in fd.readlines() ]

def add_key(filename=PUB_KEY):

    commands = (
        "mkdir -p %s;"
        "chmod 700 %s;"
        """echo "%s" >> %s;"""
        "chmod 644 %s;"
    )

    t = (SSH_HOME,SSH_HOME,_get_public_key(filename),AUTH_KEYS,AUTH_KEYS)
    command = commands % t
    run(command)
