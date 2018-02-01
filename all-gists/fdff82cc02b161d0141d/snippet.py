#!/usr/bin/env python2

"""
Queries the slowlog database table and outputs it in
the normal MySQL slow log text format.

Run this script by:
python /path/to/slow_log_dump.py dbip dbport dbusr dbpwd [start_time] [end_time] > /path/to/slow_log_dump.log

Then you can run the normal mysqldumpslow parser on the output file (slow_log_dump.log)
Example (print the top 40 slow queries by time):
mysqldumpslow -t 40 -s t /path/to/slow_log_dump.log

"""

import sys, os
import random
import time
import MySQLdb

if __name__ == "__main__":
 
    argc = len(sys.argv)
    if argc < 5:
        print "usage:%s dbip dbport dbusr dbpwd [start_time] [end_time]" % sys.argv[0]
        print "example:%s 127.0.0.1 3306 root root '2014-1-1' '2014-1-2'" % sys.argv[0]
        exit(1)
 
    dbip = sys.argv[1]
    dbport = int(sys.argv[2])
    dbusr = sys.argv[3]
    dbpwd = sys.argv[4]
    start_time = ""
    if argc > 5:
        start_time = sys.argv[5]
    end_time = ""
    if argc > 6:
    	end_time = sys.argv[6]

    try:
        # connect to mysql
    	conn = MySQLdb.connect(host=dbip, port=dbport, user=dbusr, passwd=dbpwd)
    	cursor = conn.cursor()
	if start_time == "":
	    sql = "SELECT * FROM mysql.slow_log ORDER BY start_time"
        else:
            if end_time == "":
	        sql = "SELECT * FROM mysql.slow_log where start_time >= '%s' ORDER BY start_time" % start_time
	    else:
	    	sql = "SELECT * FROM mysql.slow_log where start_time >= '%s' and start_time <= '%s' ORDER BY start_time" % (start_time, end_time)

        conn.query(sql)
        r = conn.use_result()

        while True:
            results = r.fetch_row(maxrows=100, how=1)
            if not results:
                break

            for row in results:
                qtime = row['query_time'].seconds
                row['query_time_f'] = qtime
        
                ltime = row['lock_time'].seconds
                row['lock_time_f'] = ltime
        
                if not row['sql_text'].endswith(';'):
                    row['sql_text'] += ';'
        
                print '# Time: %s' % row['start_time']
                print '# User@Host: {user_host}'.format(**row)
                print '# Query_time: {query_time_f}  Lock_time: {lock_time_f} Rows_sent: {rows_sent}  Rows_examined: {rows_examined}'.format(**row)
                print 'use {db};'.format(**row)
                print row['sql_text']

    except MySQLdb.Error, e:
        cur_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        error = "%s - Error %d: %s" % (cur_time, e.args[0], e.args[1])
        print error
        exit(-1)

    exit(0)