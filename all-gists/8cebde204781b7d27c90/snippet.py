#!/bin/env python

import timeit

loops = 1000

setup = """
import MySQLdb
db = MySQLdb.connect(host="remotedb.example.com",
                          read_default_file="/root/.my.cnf",
                          charset = "utf8", use_unicode = True)
c = db.cursor()
"""
stmt = 'c.execute("SELECT 1")'

t = timeit.Timer(stmt, setup)

total_time = t.timeit(number=loops)
print "Total loops: {}".format(loops)
print "Total time: {}".format(total_time)
print "Avg time per loop: {}".format(total_time / loops)