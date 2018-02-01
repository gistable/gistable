#!/usr/bin/python
# -*- python-mode -*-

import boto.ec2.elb
import sys

elbs = [ 'my_elb' ] # or whatever
AWS_ACCESS_KEY_ID = '' # fill this out!
AWS_SECRET_ACCESS_KEY = '' # this too!

def _name(elb):
    """Convert to a munin-compatible name"""
    return elb.replace('-', '_')

if len(sys.argv) > 1 and sys.argv[1]=='config':
    print """multigraph elb_status
graph_title Instances across all ELBs
graph_vlabel Active instances
graph_args -l 0
graph_category Other
graph_info Number of ELB instances in different states (inservice, outofservice &c)
inservice.label In service
outofservice.label Out of service

"""
    for elb in elbs:
        print """multigraph elb_status.%(elb)s
graph_title Instances in %(elb)s
graph_vlabel Active instances
graph_args -l 0
graph_category Other
graph_info Number of ELB instances in different states (inservice, outofservice &c)
inservice.label In service
inservice.warning 2:
inservice.critical 1:
outofservice.label Out of service
outofservice.warning 1

""" % { 'elb': _name(elb) }
    sys.exit(0)

# connect to EC2, find our ELBs, describe instance health for each
# and turn that into awesome data.
c = boto.ec2.elb.ELBConnection(aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

total_inservice = 0
total_outofservice = 0
for elb in elbs:
    inservice = outofservice = 0
    for instance_state in c.describe_instance_health(elb):
        if instance_state.state==u'InService':
            inservice += 1
        elif instance_state.state==u'OutOfService':
            outofservice += 1
        else:
            # eek!
            pass
    print "multigraph elb_status.%(elb)s" % { 'elb': _name(elb) }
    print "inservice.value %(count)i" % {
        'elb': _name(elb),
        'count': inservice,
        }
    print "outofservice.value %(count)i" % {
        'elb': _name(elb),
        'count': outofservice,
        }
    total_inservice += inservice
    total_outofservice += outofservice

print "multigraph elb_status"
print "inservice.value %i" % total_inservice
print "outofservice.value %i" % total_outofservice
