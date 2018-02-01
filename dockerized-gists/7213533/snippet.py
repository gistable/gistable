'''
@author Bommarito Consulting, LLC; http://bommaritollc.com/
@date 20131029
This script monitors and logs to CSV the status of all tunnels for all VPNs for a single EC2 region.
'''

# Imports
import boto
import boto.ec2
import boto.vpc
import csv
import datetime
import fabric.colors
import sys

# Set your AWS creds if you aren't using a dotfile or some other boto auth method
aws_access_key_id=None
aws_secret_access_key=None
ec2_region='us-east-1'

# CSV output file
csv_file_name = "vpn_status.csv"

def report_tunnel_down(tunnel):
	'''
	Report and possibly take corrective action.
	'''
	sys.stderr.write(fabric.colors.red("Tunnel {0} is down since {1}"\
		.format(tunnel.outside_ip_address, tunnel.last_status_change)))

def test_tunnel_status(tunnel):
	'''
	Run a test on tunnel status.
	For now, this just trusts the AWS API status and does not perform network-level test.
	'''
	# Check by status string
	if tunnel.status == 'DOWN':
		report_tunnel_down(tunnel)
		return False
	else:
		return True

def test_vpc_status():
	'''
	Output VPC tunnel statuses.
	'''
	# Create EC2 connection
	ec2_conn = boto.vpc.connect_to_region(ec2_region, 
		aws_access_key_id= aws_access_key_id,
		aws_secret_access_key=aws_secret_access_key)
	
	# Setup the CSV file writer
	with open(csv_file_name, 'a') as csv_file:
		csv_writer = csv.writer(csv_file)
		# Iterate over all VPC connections
		for vpn_connection in ec2_conn.get_all_vpn_connections():
			# Handle connection and its tunnels
			for tunnel in vpn_connection.tunnels:
				# Test the tunnel and output
				status = test_tunnel_status(tunnel)
				row = [datetime.datetime.now(), vpn_connection.id, 
					tunnel.outside_ip_address, status, 
					tunnel.status_message, tunnel.last_status_change]
				csv_writer.writerow(row)

if __name__ == "__main__":
	test_vpc_status()
