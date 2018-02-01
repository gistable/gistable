#!/usr/bin/env python
import salt.cli.caller
import salt.config
import argparse
import sys

parser = argparse.ArgumentParser(description='Check if minions are online.')
parser.add_argument('hostname', help='The name of the minion to be checked')

args = parser.parse_args()

hostname = args.hostname

opts = salt.config.minion_config("/etc/salt/minion")
opts['doc'] = False
opts['grains_run'] = False
opts['raw_out'] = False
opts['json_out'] = True
opts['txt_out'] = False
opts['yaml_out'] = False
opts['color'] = True
opts['root_dir'] = None
opts['fun'] = "publish.publish"
opts['returner'] = None
opts['arg'] = (hostname, "test.ping")

caller = salt.cli.caller.Caller(opts)
result = caller.call()

if result.get("return").get(hostname) is True:
    sys.stdout.write("OK: minion %s is online\n" % hostname)
    sys.exit(0)
else:
    sys.stderr.write("CRITICAL: minion %s is not online!\n" % hostname)
    sys.exit(2)