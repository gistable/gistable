#!/usr/bin/env python2
# Find and restart lost Juju agents in a Juju2 environment.
import subprocess
import json

juju_output = subprocess.check_output(["juju","status","--format=json"])

the_dict = json.loads(juju_output)

to_fix = {}

for app, app_info in the_dict['applications'].items():
    if 'units' in app_info:
        for unit, unit_info in app_info['units'].items():
            if unit_info['juju-status']['current'] == "lost":
                to_fix[unit] = 'jujud-unit-{}'.format(unit.replace('/', '-'))
            if 'subordinates' in unit_info:
                for sub, sub_info in unit_info['subordinates'].items():
                    if sub_info['juju-status']['current'] == "lost":
                        to_fix[sub] = 'jujud-unit-{}'.format(sub.replace('/', '-'))

for machine, machine_info in the_dict['machines'].items():
    if machine_info['juju-status']['current'] == "down":
        to_fix[machine] = 'jujud-machine-{}'.format(machine)
if not to_fix:
    print("nothing to fix, you're lucky")
for where, what in to_fix.items():
    print("Restarting {} in {}".format(what, where))
    cmd = ['juju', 'ssh', where, "sudo", "service", what, "restart"]
    subprocess.check_call(cmd)
