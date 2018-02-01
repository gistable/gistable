import boto.vpc
import time

REGION_NAME = 'us-west-2'
AMI_ID = 'ami-8e27adbe'  # Amazon Linux AMI

conn = boto.vpc.connect_to_region(REGION_NAME)

# Create a VPC
vpc = conn.create_vpc('10.0.0.0/16')

# Configure the VPC to support DNS resolution and hostname assignment
conn.modify_vpc_attribute(vpc.id, enable_dns_support=True)
conn.modify_vpc_attribute(vpc.id, enable_dns_hostnames=True)

# Create an Internet Gateway
gateway = conn.create_internet_gateway()

# Attach the Internet Gateway to our VPC
conn.attach_internet_gateway(gateway.id, vpc.id)

# Create a Route Table
route_table = conn.create_route_table(vpc.id)

# Create a size /16 subnet
subnet = conn.create_subnet(vpc.id, '10.0.0.0/24')

# Associate Route Table with our subnet
conn.associate_route_table(route_table.id, subnet.id)

# Create a Route from our Internet Gateway to the internet
route = conn.create_route(route_table.id, '0.0.0.0/0', gateway.id)

# Create a new VPC security group
sg = conn.create_security_group('pycon_group',
                                'A group for PyCon',
                                vpc.id)

# Authorize access to port 22 from anywhere
sg.authorize(ip_protocol='tcp', from_port=22, to_port=22, cidr_ip='0.0.0.0/0')

# Run an instance in our new VPC
reservation = conn.run_instances(AMI_ID, key_name='aws_mitch',
                                 security_group_ids=[sg.id],
                                 instance_type='t1.micro',
                                 subnet_id=subnet.id)
instance = reservation.instances[0]

# Now create an Elastic IP address for the instance
eip = conn.allocate_address(domain='vpc')

# And associate the EIP with our instance
conn.associate_address(instance_id=instance.id,
                       allocation_id=eip.allocation_id)

# Wait for the instance to be running and have an public DNS name
while instance.state != 'running' or not instance.public_dns_name:
    instance.update()

print(instance.public_dns_name)
