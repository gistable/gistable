#!/usr/bin/env python
import salt.client
import argparse
import sys

parser = argparse.ArgumentParser(description='Check if minions are online.')
parser.add_argument('hostname', help='The name of the minion to be checked')

args = parser.parse_args()

hostname = args.hostname

client = salt.client.LocalClient()
result = client.cmd(hostname, 'test.ping')

if result.get(hostname) is True:
    sys.stdout.write("OK: minion %s is online\n" % hostname)
    sys.exit(0)
else:
    sys.stderr.write("CRITICAL: minion %s is not online!\n" % hostname)
    sys.exit(2)