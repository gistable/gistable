#!/usr/bin/python

import boto3
import sys
import os
from urllib2 import urlopen

default_region = 'ap-southeast-2'
default_port_array = [ 80, 443 ]
default_replace_ingress = True
external_ip_query_address = 'http://ip.42.pl/raw'

def get_external_ip():
    return urlopen(external_ip_query_address).read()

def modify_security_group(security_group, ip, port_array, replace_ingress):
    cidr_ip = ip + "/32"
    print "retrieving security group info..."
    ec2 = boto3.resource('ec2')
    sg = ec2.SecurityGroup(security_group)
    if replace_ingress:
        for rule in sg.ip_permissions:
            for cidr_rule in rule['IpRanges']:
                print ("revoking ingress " + rule['IpProtocol'] + " rule for cidr ip: " + cidr_rule['CidrIp'] +
                        " from port: " + str(rule['FromPort']) + " to port: " + str(rule['ToPort']))
                sg.revoke_ingress(IpProtocol=rule['IpProtocol'], CidrIp=cidr_rule['CidrIp'],
                        FromPort=rule['FromPort'], ToPort=rule['ToPort'])
    for port in port_array:
        print "authorising ingress tcp rule for cidr ip: " + cidr_ip + " port: " + str(port)
        sg.authorize_ingress(IpProtocol='tcp', CidrIp=cidr_ip, FromPort=int(port), ToPort=int(port))

def validate_region():
    region = os.environ.get('EC2REGION')
    if region is None:
        region = default_region
    print "region is: " + region
    boto3.setup_default_session(region_name=region)

def validate_command_line():
    if len(sys.argv) > 1 and len(sys.argv) < 5:
        security_group = sys.argv[1]
        if not security_group.startswith('sg-'):
            print "checking for security group by tag value as security group does not start with 'sg-'"
            security_group = convert_security_group_name_to_id(security_group)
        if len(sys.argv) > 2:
            port_array = sys.argv[2].split(',')
            print "setting ingress for port array: " + ' '.join(port_array)
        else:
            port_array = default_port_array
        if len(sys.argv) == 4 and sys.argv[3] == '--add':
            print "adding to existing ingress rules"
            replace_ingress = False
        else:
            print "replacing existing ingress rules"
            replace_ingress = default_replace_ingress
    else:
        raise ValueError('Error: invalid number of parameters. \r\nUsage: ' + sys.argv[0] +
                ' <security-group-id|security-group-name> [port1,port2,port3,...] [--add]' )
    return security_group, port_array, replace_ingress

def convert_security_group_name_to_id(security_group):
    ec2 = boto3.client('ec2')
    response = ec2.describe_security_groups(Filters=[{ 'Name': 'tag-value', 'Values': [security_group] }])
    if response is not None:
        security_groups = response.get('SecurityGroups')
        if len(security_groups) == 1:
            security_group_id = security_groups[0].get('GroupId')
            print "security group found with id {0} for tag value {1}".format(security_group_id, security_group)
            return security_group_id
        raise ValueError('Error: more than one tag with value: {0} exists'.format(security_group))
    raise ValueError('Error: security group {0} does not exist by group-id or tag value'.format(security_group))

def main():
    """  Set security group argv[1] to current ip address for ports in argv[2] """
    try:
        print "validating region..."
        validate_region()
        print "getting external ip address..."
        ip = get_external_ip()
        print "your external ip address is: " + ip
        security_group, port_array, replace_ingress = validate_command_line()
        print "security group for modification is: " + security_group
        modify_security_group(security_group, ip, port_array, replace_ingress)
        print "done."
    except Exception as e:
        print "Exception caught: " + str(e)

if __name__ == "__main__":
    main()