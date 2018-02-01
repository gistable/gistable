#!/usr/bin/env python
"""
A nagios plugin for ensuring that load balancers have at least a certain
number of healthy nodes.

Usage:

Nagios Command:
    define command {
        command_name check_elb_healthy_hosts
        command_line /path/to/virtualenv/bin/python /path/to/nagios-plugins/check_elb_healthy_hosts.py -k $USER3$ -s $USER4$ -n $HOSTALIAS$ -w $ARG1$ -c $ARG2$
    }

Nagios Service:
    define service {
        check_command         check_elb_healthy_hosts!2:!1:
        notification_interval 0
        use                   generic-service
        service_description   elb-healthy-hosts
        hostgroup_name        elb
    }

Example Host (we use virtual hosts for ELBs; the alias (LB name) is important):
    define host {
        check_command check_http
        address       brooklynbeta-ssl-12345.us-east-1.elb.amazonaws.com
        host_name     lb_brooklynbeta-ssl-12345
        alias         brooklynbeta-ssl
        use           generic-host
        hostgroups    elb,http,https,elb-https
    }

And finally, you'll need the credentials in Nagios's resources.cfg:
    # AWS credentials (here so they can be embedded without revealing content)
    # USER3 is the AWS key ID
    # USER4 is the AWS secret access key
    $USER3$=AAABLEEPBLOOP
    $USER4$=blEeP+bloopity+rob0T+N01SE5

Boto and NagiosPlugin are available via PyPI/pip: https://pypi.python.org/pypi

"""


import os
from boto.ec2.elb import ELBConnection
import nagiosplugin
import argparse

class HealthyHosts(nagiosplugin.Resource):
    """Nagios Plugin Resource to check load balancers for the number of healthy hosts"""

    def __init__(self, elb_conn, lb_name):
        """Set up instance variables"""
        self.elb_conn = elb_conn
        self.lb_name = lb_name

    def probe(self):
        """Actually check AWS/EC2 via boto"""
        health = self.elb_conn.describe_instance_health(self.lb_name)
        healthy_count = 0
        for instance in health:
            if instance.state == 'InService':
                healthy_count += 1

        # truncates to a max of 20 characters
        return [nagiosplugin.Metric(self.lb_name[:20], healthy_count, context="hosts")]

class HealthySummary(nagiosplugin.Summary):
    """Summary class for Nagios Plugin"""

    def ok(self, results):
        """Human-readable status line"""
        return 'healthy hosts for %s' % str(results[0])


@nagiosplugin.guarded
def main():
    """Main check"""

    # Parse arguments
    argp = argparse.ArgumentParser(description="Nagios plugin to check ELB instance health")
    # outside of 2 to infinity
    argp.add_argument('-w', '--warning', metavar='RANGE', default='2:',
                      help='return warning if healthy instances is outside RANGE')
    # outside of 1 to infinity
    argp.add_argument('-c', '--critical', metavar='RANGE', default='1:',
                      help='return critical if healthy_instances is outside RANGE')
    argp.add_argument('-n', '--name', required=True, help="Load Balancer name")
    argp.add_argument('-k', '--key', required=True, help="AWS Access Key ID")
    argp.add_argument('-s', '--secret', required=True, help="AWS Secret Access Key")
    argp.add_argument('-v', '--verbose', default=False, action="store_true", help="Verbose")
    args = argp.parse_args()

    # establish EC2/ELB connection (Boto)
    elb_conn = ELBConnection(
        aws_access_key_id = args.key,
        aws_secret_access_key = args.secret
    )

    # Hook the actual nagios plugin
    check = nagiosplugin.Check(
        HealthyHosts(elb_conn, args.name),
        nagiosplugin.ScalarContext('hosts', args.warning, args.critical),
        HealthySummary())
    check.main(verbose=args.verbose)


if __name__ == '__main__':
    main()