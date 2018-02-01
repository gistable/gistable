#!/usr/bin/env python
'''
@author Luke Campbell
'''

import gevent_profiler
import time

class TimeIt(object):
    def __init__(self, message=''):
        self.message = message
    def __enter__(self):
        self.i = time.time()
    def __exit__(self, type, value, traceback):
        print '%s %ss' % (self.message or 'Took', time.time() - self.i)

class ProfileIt(object):
    def __init__(self, stats='stats.txt', summary='summary.txt'):
        self.stats   = stats
        self.summary = summary

    def __enter__(self):
        gevent_profiler.set_stats_output(self.stats)
        gevent_profiler.set_summary_output(self.summary)
        gevent_profiler.set_trace_output(None)
        gevent_profiler.attach()

    def __exit__(self, type, value, traceback):
        gevent_profiler.detach()


