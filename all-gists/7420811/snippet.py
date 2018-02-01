# Plugin for the diamond to collect stats from Riak over HTTP.
#
# Copyright (c) 2013, Metricfire Ltd (Hosted Graphite)
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Metricfire Ltd nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL METRICFIRE LTD BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import diamond.collector
import urllib2
import json

class RiakCollector(diamond.collector.Collector):
    def get_default_config_help(self):
        config_help = super(RiakCollector, self).get_default_config_help()
        config_help.update({
        })
        return config_help

    def get_default_config(self):
        """
        Returns the default collector settings
        """
        config = super(RiakCollector, self).get_default_config()
        config.update({
            'path': 'riak'
        ,   'stats_url':   'http://localhost:8098/stats/'
        ,   'http_timeout': 10
        })
        stats = """vnode_gets vnode_puts vnode_index_reads
vnode_index_writes vnode_index_writes_postings vnode_index_deletes
vnode_index_deletes_postings read_repairs vnode_gets_total vnode_puts_total
vnode_index_reads_total vnode_index_writes_total
vnode_index_writes_postings_total vnode_index_deletes_total
vnode_index_deletes_postings_total node_gets node_gets_total
node_get_fsm_time_mean node_get_fsm_time_median node_get_fsm_time_95
node_get_fsm_time_99 node_get_fsm_time_100 node_puts node_puts_total
node_put_fsm_time_mean node_put_fsm_time_median node_put_fsm_time_95
node_put_fsm_time_99 node_put_fsm_time_100 node_get_fsm_siblings_mean
node_get_fsm_siblings_median node_get_fsm_siblings_95 node_get_fsm_siblings_99
node_get_fsm_siblings_100 node_get_fsm_objsize_mean node_get_fsm_objsize_median
node_get_fsm_objsize_95 node_get_fsm_objsize_99 node_get_fsm_objsize_100
read_repairs_total coord_redirs_total precommit_fail postcommit_fail mem_total
mem_allocated sys_process_count pbc_connects_total pbc_connects pbc_active
executing_mappers memory_total memory_processes memory_processes_used
memory_system memory_atom memory_atom_used memory_binary memory_code memory_ets
ignored_gossip_total rings_reconciled_total rings_reconciled gossip_received
handoff_timeouts riak_kv_vnodes_running riak_kv_vnodeq_min
riak_kv_vnodeq_median riak_kv_vnodeq_mean riak_kv_vnodeq_max
riak_kv_vnodeq_total riak_pipe_vnodes_running riak_pipe_vnodeq_min
riak_pipe_vnodeq_median riak_pipe_vnodeq_mean riak_pipe_vnodeq_max
riak_pipe_vnodeq_total"""
        config['stats'] = map(lambda stat: stat.strip(), stats.replace("\n", " ").split(" "))
        return config

    def collect(self):
        stats = json.loads(urllib2.urlopen(self.config['stats_url'], timeout = self.config['http_timeout']).read())

        # Publish all the stats in the config list.
        for key, value in stats.iteritems():
            if key in self.config['stats']:
                self.publish(key, value)
