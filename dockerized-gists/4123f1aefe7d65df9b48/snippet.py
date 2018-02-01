import skew

# Add whitelisted CIDR blocks here, e.g. 192.168.1.1/32.
# Any addresses not in this list will be flagged.
whitelist = []

for secgrp in skew.scan('arn:aws:ec2:*:*:security-group/*'):
    for ipperms in secgrp.data['IpPermissions']:
        for ip in ipperms['IpRanges']:
            if ip['CidrIp'] not in whitelist:
                print('%s: %s is not whitelisted' % (sg.arn, ip['CidrIp']))