from boto.ec2 import connect_to_region

ec2 = connect_to_region('us-west-1')
target = '127.0.0.1/32'
remove = False

sgs = ec2.get_all_security_groups()

for sg in sgs:
	for rule in sg.rules:
		for grant in rule.grants:
			if target == grant.cidr_ip:
				print "target found in sg {sg}".format(sg=sg.name)
				if remove:
					print "removing"
					sg.revoke(
						ip_protocol=rule.ip_protocol,
						from_port=rule.from_port,
						to_port=rule.from_port,
						cidr_ip=target
					)
