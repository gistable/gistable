#!/usr/bin/env python
"""
Nagios plugin to check PostgreSQL 9 streaming replication lag.

Requires psycopg2 and nagiosplugin (both installable with pip/easy_install).

MIT licensed:

    Copyright (c) 2010 Jacob Kaplan-Moss. All rights reserved.

    Permission is hereby granted, free of charge, to any person obtaining a
    copy of this software and associated documentation files (the
    "Software"), to deal in the Software without restriction, including
    without limitation the rights to use, copy, modify, merge, publish,
    distribute, sublicense, and/or sell copies of the Software, and to
    permit persons to whom the Software is furnished to do so, subject to
    the following conditions:

    The above copyright notice and this permission notice shall be included
    in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
    OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
    CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
    TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
    SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

import nagiosplugin
import psycopg2

__version__ = '1.0'

class StreamingReplicationCheck(nagiosplugin.Check):
    
    def __init__(self, optparser, log):
        optparser.description = "Check PG9 streaming replication lag."
        optparser.version = __version__
        optparser.add_option('-M', '--master',
            metavar='DSN',
            help='DSN for the master connection (e.g. "host=foo user=bar")'
        )
        optparser.add_option('-S', '--slave',
            metavar='DSN',
            help='DSN for the slave connection (e.g. "host=foo user=bar")'
        )
        optparser.add_option('-w', '--warning',
            default='128',
            metavar='WARN',
            help='warn if replication lags by WARN kbytes (default: 64).'
        )
        optparser.add_option('-c', '--critical',
            default='512',
            metavar='CRIT',
            help='warn if replication lags by CRIT kbytes (default: 256).'
        )
        
    def process_args(self, opts, args):
        self.master_conn = psycopg2.connect(opts.master)
        self.slave_conn = psycopg2.connect(opts.slave)
        self.warning = opts.warning
        self.critical = opts.critical
    
    def obtain_data(self):
        mc = self.master_conn.cursor()
        mc.execute('SELECT pg_current_xlog_location()')
        master_loc = xlog_to_bytes(mc.fetchone()[0])
        self.master_conn.commit()
        self.master_conn.close()
        
        sc = self.slave_conn.cursor()
        sc.execute('SELECT pg_last_xlog_replay_location()')
        slave_loc = xlog_to_bytes(sc.fetchone()[0])
        self.slave_conn.commit()
        self.slave_conn.close()
        
        self.lag = (master_loc - slave_loc) / 1024
        self.measures = [
            nagiosplugin.Measure('lag', self.lag, 'kB', self.warning, self.critical)
        ]
        
    def default_message(self):
        return "lag is %s kB" % self.lag
        
def xlog_to_bytes(xlog):
    """
    Convert an xlog number like '0/C6321D98' to an integer representing the
    number of bytes into the xlog.
    
    Logic here is taken from 
    https://github.com/mhagander/munin-plugins/blob/master/postgres/postgres_streaming_.in.
    I assume it's correct...
    """
    logid, offset = xlog.split('/')
    return (int('ffffffff', 16) * int(logid, 16)) + int(offset, 16)
    
if __name__ == '__main__':
    nagiosplugin.Controller(StreamingReplicationCheck)()