#!/usr/bin/env python
'''
This script should be run against an ansible Inventory file
in order to return host/group information
Contact guy dot matz dot cft at jcrew dot com with any questions, although he's 
probably completely forgotten everything about this . ..   :-(
'''

import os
import json
import sys
from optparse import OptionParser
import ansible.inventory
import random

parser = OptionParser()
parser.add_option("-i", "--invfile", dest="invfile", help="Location of inventory file", metavar="FILE")
parser.add_option("-g", "--group", dest="group", help="Group to search for", metavar="ANSIBLE_GROUP")
parser.add_option("-n", "--node", dest="node", help="Host/Node to search for", metavar="ANSIBLE_HOST")
parser.add_option("-j", "--jc_env", dest="jc_env", help="JCrew environment, e.g. steel", metavar="JC_ENV")
parser.add_option("-r", "--return", dest="return_method", help="Thingy to return", metavar="RETURN_METHOD")
parser.add_option("-d", "--debug", dest="debug", help="debug output")

(options, args) = parser.parse_args()
invfile = options.invfile
node = options.node
group = options.group
return_method = options.return_method
jc_env = options.jc_env
debug = options.debug

class jcInventory(ansible.inventory.Inventory):

    def __init__(self, *args, **kw):
        ansible.inventory.Inventory.__init__(self, *args, **kw)

    def groups2str(self, groups, node=options.node):
        if len(groups) == 0:
            raise Exception('No groups found for %s' % node)
        s = "{\n"
        for g in groups:
            s += '"%s" => ["%s"],\n' % (g, node)

        s+= "\n}"
        return s

    def hosts_in_group(self, group=options.group):
        return [ h.name for h in self.get_group(group).get_hosts() ]

    def random_host_in_group(self, group=options.group):
        from random import choice
        group_hosts = self.hosts_in_group(group)
        rhost = choice(group_hosts)
        return rhost
 
    def base_groups(self):
        groups = [ g.name for g in self.groups if g.name not in [jc_env,'ungrouped','all'] ] 
        return groups
 
    def most_base_groups(self, jc_env = options.jc_env):
        groups = [ g.name for g in self.groups if g.name not in ['ungrouped','all'] ] 
        return groups
 
    def all_base_groups(self):
        groups = [ g.name for g in self.groups ] 
        return groups

    def groups_for_node(self, node=options.node, jc_env=options.jc_env):
        groups = [ g.name for g in self.groups_for_host(node)
                              if g.name not in [jc_env, 'ungrouped', 'all'] ]
        return groups

    def most_groups_for_node(self, node=options.node):
        groups = [ g.name for g in self.groups_for_host(node)
                              if g.name not in ['ungrouped', 'all'] ]
        return groups

    def all_groups_for_node(self, node=options.node):
        groups = [ g.name for g in self.groups_for_host(node) ]
        return groups
 
def main():
    i = jcInventory(invfile)
    idata = getattr(i, return_method)()
    if debug:
        print json.dumps(i.inv_data)
    if type(idata) is str:
        print idata
    elif type(idata) in [list, set]:
        for e in idata:
            print e
    else:
        print json.dumps(idata)

if __name__ == '__main__':
    usage = '%s -i inventory_file [-g group ] [-n node] [-j env] [-r method_to_run ] [-d ]' % sys.argv[0]
    if not invfile or not return_method:
        print "I need at least an inventory file and a return_method!"
        print usage
        sys.exit(1)
    main()
