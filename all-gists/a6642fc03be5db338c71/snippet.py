# poodle_shave.py
# It is YOUR responsibility to stop POODLE attacks by disabling SSLv3!

import os
import sys
import boto.ec2.elb

try:
    os.environ["AWS_ACCESS_KEY_ID"]
    os.environ["AWS_SECRET_ACCESS_KEY"]
    os.environ["AWS_DEFAULT_REGION"]
except KeyError:
    print "Please set the AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_DEFAULT_REGION env vars"
    sys.exit(1)

port = 443

conn = boto.ec2.elb.connect_to_region(os.environ["AWS_DEFAULT_REGION"])
elbs = conn.get_all_load_balancers()
for elb in elbs:
    print "Starting on %s" % elb.name
    conn.create_lb_policy(elb.name,
        "PoodleShaveSSLNegotiationPolicy",
        "SSLNegotiationPolicyType",
        {"Reference-Security-Policy": "ELBSecurityPolicy-2014-10"})
    print "Setting policy"
    conn.set_lb_policies_of_listener(elb.name, port, ["PoodleShaveSSLNegotiationPolicy"])
    print "Done with %s!" % elb.name