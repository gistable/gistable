#!/usr/bin/env python
import argparse
import re
import os
import subprocess

try:
    import json
except ImportError:
    import simplejson as json


def get_running_vms():
    """
    Returns the list of ids for the VMs currently running in VirtualBox.
    """
    output = subprocess.Popen(['VBoxManage', 'list', 'runningvms'], stdout=subprocess.PIPE).communicate()[0]
    vms = []
    if output is not None:
        lines = output.split('\n')
        for line in lines:
            pattern = re.compile(r'.*{(.*)}')
            match = pattern.match(line)
            if match:
                vms.append(match.group(1))
    return vms


def poweroff_vm(vm_id):
    """
    Issues a 'poweroff' command to VirtualBox for the given VM.
    """
    print "Powering off VM: %s..." % vm_id
    subprocess.call(['VBoxManage', 'controlvm', vm_id, 'poweroff'])


def find_machines_dir():
    """
    Walks up from the current path untils it finds a '.vagrant/machines/' directory.
    """
    path = os.getcwd()
    while path != '/':
        machines_dir = os.path.join(path, '.vagrant/machines/')
        if os.path.isdir(machines_dir):
            return machines_dir
        # Try one level up
        path = os.path.abspath(os.path.join(path, os.pardir))

def find_vm_ids(machines_dir):
    """
    Returns all the VM id files found under the given .vagrant/machines/ directory.
    """
    matches = []
    for root, dirnames, filenames in os.walk(machines_dir):
        for filename in filenames:
            if filename == 'id':
                matches.append(os.path.join(root, filename))
    return matches


# Parse the command's arguments
parser = argparse.ArgumentParser()
parser.add_argument('--all', action='store_true')
args = parser.parse_args()

running_vms = get_running_vms()

if args.all:
    if len(running_vms):
        print "%s VM(s) currently running..." % len(running_vms)
        for vm in running_vms:
            poweroff_vm(vm)
    else:
        print "No VMs are currently running."
else:
    machines_dir = find_machines_dir()
    if machines_dir:
        for vm_id in find_vm_ids(machines_dir):
            vm_id = open(vm_id).read()
            if vm_id in running_vms:
                poweroff_vm(vm_id)
            else:
                print "VM %s is already powered off." % vm_id
    else:
        print "Cannot find any '.vagrant/machines/' directory..."