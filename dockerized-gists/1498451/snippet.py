#!/usr/bin/env python
"""
Recipe for creating and updating security groups programmatically.


"""

import collections

import boto


# Follow instruction at http://www.datastax.com/docs/1.0/install/install_ami
# to define the cluster security group rules and client security group rules.
SecurityGroupRule = collections.namedtuple("SecurityGroupRule", ["ip_protocol", "from_port", "to_port", "cidr_ip", "src_group_name"])

CASSANDRA_RULES = [
    SecurityGroupRule("tcp", "22", "22", "0.0.0.0/0", None),
    SecurityGroupRule("tcp", "1024", "65535", "0.0.0.0/0", "Cassandra Cluster"),
    SecurityGroupRule("tcp", "7000", "7000", "0.0.0.0/0", "Cassandra Cluster"),
    SecurityGroupRule("tcp", "61620", "61621", "0.0.0.0/0", "Cassandra Cluster"),
    SecurityGroupRule("tcp", "7199", "7199", "0.0.0.0/0", None),
    SecurityGroupRule("tcp", "8888", "8888", "0.0.0.0/0", None),
    SecurityGroupRule("tcp", "8983", "8983", "0.0.0.0/0", None),
    SecurityGroupRule("tcp", "9160", "9160", "0.0.0.0/0", None),
]

TEST_RULES = [
    # ssh makes life possible
    SecurityGroupRule("tcp", "22", "22", "0.0.0.0/0", None),
]

SECURITY_GROUPS = [("Cassandra Cluster", CASSANDRA_RULES),
                   ("Test", TEST_RULES)
                   ]


def get_or_create_security_group(c, group_name, description=""):
    """
    """
    groups = [g for g in c.get_all_security_groups() if g.name == group_name]
    group = groups[0] if groups else None
    if not group:
        print "Creating group '%s'..."%(group_name,)
        group = c.create_security_group(group_name, "A group for %s"%(group_name,))
    return group


def modify_sg(c, group, rule, authorize=False, revoke=False):
    src_group = None
    if rule.src_group_name:
        src_group = c.get_all_security_groups([rule.src_group_name,])[0]

    if authorize and not revoke:
        print "Authorizing missing rule %s..."%(rule,)
        group.authorize(ip_protocol=rule.ip_protocol,
                        from_port=rule.from_port,
                        to_port=rule.to_port,
                        cidr_ip=rule.cidr_ip,
                        src_group=src_group)
    elif not authorize and revoke:
        print "Revoking unexpected rule %s..."%(rule,)
        group.revoke(ip_protocol=rule.ip_protocol,
                     from_port=rule.from_port,
                     to_port=rule.to_port,
                     cidr_ip=rule.cidr_ip,
                     src_group=src_group)


def authorize(c, group, rule):
    """Authorize `rule` on `group`."""
    return modify_sg(c, group, rule, authorize=True)


def revoke(c, group, rule):
    """Revoke `rule` on `group`."""
    return modify_sg(c, group, rule, revoke=True)


def update_security_group(c, group, expected_rules):
    """
    """
    print 'Updating group "%s"...'%(group.name,)
    import pprint
    print "Expected Rules:"
    pprint.pprint(expected_rules)

    current_rules = []
    for rule in group.rules:
        if not rule.grants[0].cidr_ip:
            current_rule = SecurityGroupRule(rule.ip_protocol,
                              rule.from_port,
                              rule.to_port,
                              "0.0.0.0/0",
                              rule.grants[0].name)
        else:
            current_rule = SecurityGroupRule(rule.ip_protocol,
                              rule.from_port,
                              rule.to_port,
                              rule.grants[0].cidr_ip,
                              None)

        if current_rule not in expected_rules:
            revoke(c, group, current_rule)
        else:
            current_rules.append(current_rule)

    print "Current Rules:"
    pprint.pprint(current_rules)

    for rule in expected_rules:
        if rule not in current_rules:
            authorize(c, group, rule)


def create_security_groups():
    """
    attempts to be idempotent:

    if the sg does not exist create it,
    otherwise just check that the security group contains the rules
    we expect it to contain and updates it if it does not.
    """
    c = boto.connect_ec2()
    for group_name, rules in SECURITY_GROUPS:
        group = get_or_create_security_group(c, group_name)
        update_security_group(c, group, rules)


if __name__=="__main__":
    create_security_groups()
