from starcluster import config
from starcluster import cluster
cfg = config.StarClusterConfig().load()
ec2 = cfg.get_easy_ec2()
cm = cluster.ClusterManager(cfg, ec2=ec2)
cl = cm.get_cluster("your_running_cluster_tag")
print len(cl.running_nodes)
