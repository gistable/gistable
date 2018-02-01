#!/usr/bin/python2.7
"""
check_solr_cloud.py

Nagios plugin for checking the status of a SolrCloud instance by
examining the clusterstate.json file on zookeeper.

Usage:

check_solr_cloud.py --zkhosts=<zookeeper hosts> --collection=<collection>

    zkhosts: Comma-delimited list of zookeeper hosts with port numbers
    collection: Solr collection to check
"""

import argparse
import json
import kazoo.client
import sys

# At least 1 active node per shard
# Only 1 active leader per shard
# Leader is active

# Config
ZK_HOSTS = 'localhost:9001'
SOLR_INDEX = 'index'

# Exit codes
STATE_OK = 0
STATE_WARNING = 1
STATE_CRITICAL = 2
STATE_UNKNOWN = 3

STATE_STR_OK = 'SOLR CLOUD OK'
STATE_STR_WARNING = 'SOLR CLOUD WARNING'
STATE_STR_CRITICAL = 'SOLR CLOUD CRITICAL'
STATE_STR_UNKNOWN = 'SOLR CLOUD UNKNOWN'

def exit_ok(message=None):
    if message:
        print "%s: %s" % (STATE_STR_OK, message)
    else:
        print STATE_STR_OK
    sys.exit(STATE_OK)

def exit_warning(message):
    print "%s: %s" % (STATE_STR_WARNING, message)
    sys.exit(STATE_WARNING)

def exit_critical(message):
    print "%s: %s" % (STATE_STR_CRITICAL, message)
    sys.exit(STATE_CRITICAL)


def main(zk_host, collection):
    try:
        zk_client = kazoo.client.KazooClient(hosts=zk_host, read_only=True)
        zk_client.start(timeout=5)
    except kazoo.handlers.threading.TimeoutError:
        exit_critical("Unable to connect to zookeeper hosts")

    try:
        cluster_state_str = zk_client.get('/clusterstate.json')[0]
    except kazoo.exceptions.NoNodeError:
        exit_critical("clusterstate.json file missing from zookeeper")

    cluster_state = json.loads(cluster_state_str)

    for shard, shard_data in cluster_state[collection]['shards'].iteritems():
        at_least_one_active_node = False
        one_leader = False
        for replica, replica_data in shard_data['replicas'].iteritems():
            if replica_data['state'] == 'active':
                at_least_one_active_node = True
            if 'leader' in replica_data and replica_data['leader'] == 'true':
                if one_leader:
                    exit_critical("More than one leader for shard: %s" % shard)
                else:
                    one_leader = True
        if not at_least_one_active_node:
            exit_critical("No active nodes for shard: %s" % shard)
        if not one_leader:
            exit_critical("No leader for shard: %s" % shard)

    zk_client.stop()

    exit_ok()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--zkhosts', required=True)
    parser.add_argument('--collection', required=True)

    args = parser.parse_args()

    main(args.zkhosts, args.collection)
