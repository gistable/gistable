#!/usr/bin/env python

import sys
import os
import json
import argparse
import collections

__description__ = """Ansible Dynamic Inventory for Terraform."""
__epilog__      = """
The environment variable `TERRAFORM_TFSTATE` must point to the
location of the Terraform state file to use.
"""
parser = argparse.ArgumentParser(description=__description__,
                                 epilog=__epilog__)
parser.add_argument("--list", action="store_true", default=False)
parser.add_argument("--host", action="store", dest='host')
args = parser.parse_args()

if 'TERRAFORM_TFSTATE' in os.environ:
    state_file = os.environ['TERRAFORM_TFSTATE']
else:
    print("The environment variable `TERRAFORM_TFSTATE` must be set.")
    exit(1)

try:
    with open(state_file) as f:
        state = json.loads(f.read())
except IOError as e:
    print("No state file found at '%s'" % state_file)
    exit(1)

inventory = collections.defaultdict(dict)
inventory["_meta"]["hostvars"] = {}

for m in state["modules"]:
    module = m["path"].pop()
    for k, attrs in m["resources"].items():
        if k.startswith("aws_instance."):
            attributes = attrs["primary"]["attributes"]
            addressable_host = attributes["private_ip"]

            name = attributes["tags.Name"]
            role = attributes["tags.Group"]

            if "tags.Mode" in attributes:
                mode = attributes["tags.Mode"].lower()
                if "hosts" not in inventory[mode]:
                    inventory[mode]["hosts"] = []

            if "hosts" not in inventory[name]:
                inventory[name]["hosts"] = []

            if "hosts" not in inventory[role]:
                inventory[role]["hosts"] = []

            inventory[name]["hosts"].append(addressable_host)
            inventory[name]["hosts"] = list(set(inventory[name]["hosts"]))

            inventory[role]["hosts"].append(addressable_host)
            inventory[role]["hosts"] = list(set(inventory[role]["hosts"]))
            
            if "tags.Mode" in attributes:
                inventory[mode]["hosts"].append(addressable_host)
                inventory[mode]["hosts"] = list(set(inventory[mode]["hosts"]))

            inventory["_meta"]["hostvars"][addressable_host] = attributes

if args.list:
    print(json.dumps(inventory, indent=3))
    exit(0)
elif args.host:
    print(json.dumps(inventory['_meta']['hostvars'][args.host], indent=3))
    exit(0)
else:
    parser.print_help()
    exit(1)
