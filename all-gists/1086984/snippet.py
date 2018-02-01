"""
The MIT License (MIT)
Copyright (c) 2011 Numan Sachwani

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import boto.ec2

from boto.ec2.elb import ELBConnection
from boto.ec2.elb import HealthCheck

from boto.ec2.autoscale import AutoScaleConnection
from boto.ec2.autoscale import LaunchConfiguration
from boto.ec2.autoscale import AutoScalingGroup
from boto.ec2.autoscale import ScalingPolicy

##############################CONFIGURATION#######################################
"""
This section is for configuring the rest of the script.
This script will do 3 things:
1. Setup a new Elastic Load Balancer
2. Create an Auto Scaling Group and configure it with an Launch Configuration
3. Create Policies for Scaling Up and Scaling Down
"""
AWS_ACCESS_KEY = '' #Your access key
AWS_SECRET_KEY = '' #Your secret key

region = 'us-east-1' #The region you want to connect to

elastic_load_balancer = {
    'name': 'my-lb',#The name of your load balancer
    'health_check_target': 'HTTP:80/index.html',#Location to perform health checks
    'connection_forwarding': [(80, 80, 'http'), (443, 443, 'tcp')],#[Load Balancer Port, EC2 Instance Port, Protocol]
    'timeout': 3, #Number of seconds to wait for a response from a ping
    'interval': 20 #Number of seconds between health checks
}

autoscaling_group = {
    'name': 'my-autoscaling-group',#descriptive name for your auto scaling group
    'min_size': 1,#Minimum number of instances that should be running at all times
    'max_size': 1 #Maximum number of instances that should be running at all times

}

lc_name = 'my-launch-config' #Descriptive name for your launch configuration

#=================AMI to launch======================================================
as_ami = {
    'id': 'ami-8e1fece7', #The AMI ID of the instance your Auto Scaling group will launch
    'access_key': 'as-ami-ec2key', #The key the EC2 instance will be configured with
    'security_groups': ['as-ami-webserver'], #The security group(s) your instances will belong to
    'instance_type': 't1.micro', #The size of instance that will be launched
    'instance_monitoring': True #Indicated whether the instances will be launched with detailed monitoring enabled. Needed to enable CloudWatch
}

##############################END CONFIGURATION#######################################

#=================Construct a list of all availability zones for your region=========
conn_reg = boto.ec2.connect_to_region(region_name=region)
zones = conn_reg.get_all_zones()

zoneStrings = []
for zone in zones:
    zoneStrings.append(zone.name)


conn_elb = ELBConnection(AWS_ACCESS_KEY, AWS_SECRET_KEY)
conn_as = AutoScaleConnection(AWS_ACCESS_KEY, AWS_SECRET_KEY)

#=================Create a Load Balancer=============================================
#For a complete list of options see http://boto.cloudhackers.com/ref/ec2.html#module-boto.ec2.elb.healthcheck
hc = HealthCheck('healthCheck',
                     interval=elastic_load_balancer['interval'],
                     target=elastic_load_balancer['health_check_target'],
                     timeout=elastic_load_balancer['timeout'])

#For a complete list of options see http://boto.cloudhackers.com/ref/ec2.html#boto.ec2.elb.ELBConnection.create_load_balancer
lb = conn_elb.create_load_balancer(elastic_load_balancer['name'],
                                       zoneStrings,
                                       elastic_load_balancer['connection_forwarding'])

lb.configure_health_check(hc)

#DNS name for your new load balancer
print "Map the CNAME of your website to: %s" % (lb.dns_name)

#=================Create a Auto Scaling Group and a Launch Configuration=============================================
#For a complete list of options see http://boto.cloudhackers.com/ref/ec2.html#boto.ec2.autoscale.launchconfig.LaunchConfiguration
lc = LaunchConfiguration(name=lc_name, image_id=as_ami['id'],
                             key_name=as_ami['access_key'],
                             security_groups=as_ami['security_groups'],
                             instance_type=as_ami['instance_type'],
                             instance_monitoring=as_ami['instance_monitoring'])
conn_as.create_launch_configuration(lc)

#For a complete list of options see http://boto.cloudhackers.com/ref/ec2.html#boto.ec2.autoscale.group.AutoScalingGroup
ag = AutoScalingGroup(group_name=autoscaling_group['name'], load_balancers=[elastic_load_balancer['name']],
                          availability_zones=zoneStrings,
                          launch_config=lc, min_size=autoscaling_group['min_size'], max_size=autoscaling_group['max_size'])
conn_as.create_auto_scaling_group(ag)


#=================Create Scaling Policies=============================================
#Policy for scaling the number of servers up and down
#For a complete list of options see http://boto.cloudhackers.com/ref/ec2.html#boto.ec2.autoscale.policy.ScalingPolicy
scalingUpPolicy = ScalingPolicy(name='webserverScaleUpPolicy',
                                              adjustment_type='ChangeInCapacity',
                                              as_name=ag.name,
                                              scaling_adjustment=2,
                                              cooldown=180)

scalingDownPolicy = ScalingPolicy(name='webserverScaleDownPolicy',
                                              adjustment_type='ChangeInCapacity',
                                              as_name=ag.name,
                                              scaling_adjustment=-1,
                                              cooldown=180)

conn_as.create_scaling_policy(scalingUpPolicy)
conn_as.create_scaling_policy(scalingDownPolicy)
