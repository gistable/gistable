#!/usr/bin/env python
import sys
import subprocess
import re
import string
try:
    import json
except:
    import simplejson as json


def get_vm_ip(vmxfile):
    ''' Return the IP of a running VM '''
    vmrun = '/Applications/VMware Fusion.app/Contents/Library/vmrun'
    try:
        ip = subprocess.check_output([vmrun, 'getGuestIPAddress', vmxfile]).strip()
        return ip
    except Exception, error:
        return None


def list_running_vms():
    ''' List the running VMs '''
    vmrun = "/Applications/VMware Fusion.app/Contents/Library/vmrun"
    output = subprocess.check_output( [vmrun, "list"]).split('\n')

    vms = []

    for line in output:
        matcher = re.search("\.vmx$", line)
        if matcher:
            vms.append(matcher.string)

    return vms

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage:"
        print sys.argv[0], " --list"
        sys.exit(1)

    vmname = re.compile(".+ / (.+) \.vmx",re.X)
    hosts = { 'fusion': [] }

    vms = list_running_vms()
    for vm in vms:
        name = vmname.match(vm).group(1)
        hosts['fusion'].append(get_vm_ip(vm))

    print json.dumps(hosts)
