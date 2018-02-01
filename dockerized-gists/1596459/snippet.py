import boto

elb = boto.connect_elb()
ec2 = boto.connect_ec2()

load_balancers = elb.get_all_load_balancers()

#
# The InstanceInfo object in the LoadBalancer object contains only a small subset
# of information about the Instance.  To get the full set of information, you have
# to retrieve the full Instance object.
# Let's retrieve the full Instance information for all instances associated with the
# first load balancer in the list

instance_ids = [i.id for i in load_balancers[0].instances]
reservations = ec2.get_all_instances(instance_ids)
instances = [r.instances[0] for r in reservations]

# instances now contains the complete Instance object for each instance object
# in the first load balancer.