import time

from boto.ec2.autoscale import AutoScaleConnection


def find_unused_launch_configs():
    conn = AutoScaleConnection()
    autoscale_groups = conn.get_all_groups(max_records=100)
    launch_configs = conn.get_all_launch_configurations(max_records=100)
    launch_config_names = {lc.name for lc in launch_configs}
    used_launch_config_names = {asg.launch_config_name for asg in autoscale_groups}
    unused_launch_config_names = launch_config_names - used_launch_config_names

    print "Autoscale Groups and Current Launch Configs:"
    print "{:<40}{:<40}".format("ASG", "LC")
    for asg in autoscale_groups:
        #print "asg:", asg.name, "-> lc:", asg.launch_config_name
        print "{:<40}{:<40}".format(asg.name, asg.launch_config_name)

    print "\nUnused Launch Configs: (launch configs without a autoscale group)"
    unused_launch_config_names = list(sorted(unused_launch_config_names))
    for unused_launch_config in unused_launch_config_names:
        print "\t", unused_launch_config
    return unused_launch_config_names


def cleanup_unused_launch_configs(unused_launch_config_names, delete=False):
    conn = AutoScaleConnection()
    configs = conn.get_all_launch_configurations(names=unused_launch_config_names)
    print "\nGetting ready to cleanup launch configs ... {}".format(delete and "FOR REAL" or "DRYRUN")
    for config in configs:
        if delete:
            print "deleting launch config: {} in {} seconds...".format(config.name, 5)
            time.sleep(5)
            print "deleting launch config: {}!".format(config.name)
            response = config.delete()
            print "deleted launch config: {} ({})!".format(config.name, response)
        else:
            print "dry run: not deleting config:", config.name


if __name__=="__main__":
    names = find_unused_launch_configs()
    if names:
        cleanup_unused_launch_configs(names, delete=True)
    else:
        print "\nNo unused launch configs!  Launch Config Janitor is going to go take a nap..."
