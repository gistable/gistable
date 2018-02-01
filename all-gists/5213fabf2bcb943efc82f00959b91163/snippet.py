#!/usr/bin/python2

#####
#
# Description
# -----------
#
# This is an Ansible dynamic inventory script that reads any Ansible hosts file
# and transforms it into the JSON data structure.
#
# Author
# ------
#
# Jiri Tyr <jiri.tyr@gmail.com>
#
#####

from ansible.utils.shlex import shlex_split
from ansible.inventory.ini import InventoryParser

import argparse
import json
import os
import sys


class MyInventoryParser(InventoryParser):
    def __init__(self):
        pass


def msg(_type, text, exit=0):
    sys.stderr.write("%s: %s\n" % (_type, text))
    sys.exit(exit)


def main():
    # Read command line options
    parser = argparse.ArgumentParser(
        description=(
            'Dynamic inventory script that reads inventory file in the INI '
            'format.'))
    parser.add_argument(
        '--filename',
        metavar='filename',
        required=True,
        help='Path to the inventory file')
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all groups and hosts')
    args = parser.parse_args()

    # Get the filename from the command line arguments
    filename = args.filename

    try:
        f = open(filename)
    except Exception as e:
        msg('E', 'Cannot open inventory file %s. %s' % (filename, str(e)))

    # Some default values
    data = {}
    group = None
    state = None
    mip = MyInventoryParser()

    # Walk through the file and build the data structure
    for line in f:
        line = line.strip()

        # Skip comments and empty lines
        if line.startswith('#') or line.startswith(';') or len(line) == 0:
            continue

        if line.startswith('['):
            # Parse group
            section = line[1:-1]

            if ':' in line:
                group, state = line[1:-1].split(':')
            else:
                group = section
                state = 'hosts'

            if group not in data:
                data[group] = {}

            if state not in data[group]:
                if state == 'vars':
                    data[group][state] = {}
                else:
                    data[group][state] = []
        else:
            # Parse hosts or group members/vars
            try:
                tokens = shlex_split(line, comments=True)
            except ValueError as e:
                msg('E', "Error parsing host definition '%s': %s" % (line, e))

            (hostnames, port) = mip._expand_hostpattern(tokens[0])

            # Create 'all' group if no group was defined yet
            if group is None:
                group = 'all'
                state = 'hosts'
                data['all'] = {
                    'hosts': []
                }

            tok = []

            if state == 'hosts':
                tok = tokens[1:]
            elif state == 'vars':
                tok = tokens

            variables = {}

            for t in tok:
                if '=' not in t:
                    msg(
                        'E',
                        "Expected key=value host variable assignment, "
                        "got: %s" % (t))

                (k, v) = t.split('=', 1)
                variables[k] = mip._parse_value(v)

            if state == 'vars':
                for key, val in variables.iteritems():
                    data[group][state][key] = val
            else:
                for host in hostnames:
                    data[group][state].append(host)

                    if state == 'hosts' and len(variables):
                        if '_meta' not in data:
                            data['_meta'] = {
                                'hostvars': {}
                            }

                        data['_meta']['hostvars'][host] = {}

                        for key, val in variables.iteritems():
                            data['_meta']['hostvars'][host][key] = val

    print(json.dumps(data, sort_keys=True, indent=2))

    try:
        f.close()
    except IOError as e:
        msg('E', 'Cannot close inventory file %s. %s' % (filename, str(e)))


if __name__ == '__main__':
    main()
