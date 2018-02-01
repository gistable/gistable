#!/usr/bin/env python
# encoding: UTF-8

"""DoubanServiceBench"""

__author__ = "Qiangning Hong <hongqn@gmail.com>"
__version__ = "$Revision: 51434 $"
__date__ = "$Date: 2010-11-17 17:44:38 +0800 (Wed, 17 Nov 2010) $"

import sys
import logging
import eventlet
import time
import math

eventlet.monkey_patch()
logger = logging.getLogger()

def main(service_name, function_name, args, options):
    module = __import__(service_name+'_client', globals(), locals())
    Client = module.Client
    if options.host:
        Client.host = options.host
    if options.port:
        Client.port = options.port

    print "This is DoubanServiceBench, Version 0.1 <$Revision: 51434 $>"
    print "Copyright 2010 Qiangning Hong, Douban Inc., http://www.douban.com/"
    print
    sys.stdout.write("Benchmarking {0} (be patient)...".format(service_name))
    sys.stdout.flush()

    start_time = time.time()
    n_failed = [0]  # use list so that test() can modify it
    times = []
    reqs = [options.requests]
    pyargs = []
    for arg in args:
        try:
            arg = eval(arg, vars(module))
        except Exception:
            arg = str(arg)
        pyargs.append(arg)

    def test():
        client = Client()
        func = getattr(client, function_name)
        while reqs[0] > 0:
            reqs[0] -= 1
            try:
                t1 = time.time()
                func(*pyargs)
            except Exception:
                n_failed[0] += 1
            finally:
                times.append(time.time() - t1)

    pool = eventlet.greenpool.GreenPool(options.concurrency)
    for i in xrange(options.concurrency):
        pool.spawn(test)
    pool.waitall()

    end_time = time.time()

    n_failed = n_failed[0]

    client = Client()
    server = client.server_software()

    print "done"
    print
    print

    times = [t*1000 for t in times]
    time_cost = end_time - start_time

    def print_result(field, value):
        print "{0:24}{1}".format(field+':', value)

    print_result("Server Software", server)
    print_result("Server Hostname", client.host)
    print_result("Server Port", client.port)
    print

    print_result("Service Name", service_name)
    print_result("Function Name", function_name)
    print

    print_result("Concurrency Level", options.concurrency)
    print_result("Time taken for tests", "{0:.3f} seconds".format(time_cost))
    print_result("Complete requests", options.requests - n_failed)
    print_result("Faild requests", n_failed)
    print_result("Requests per seconds",
                 "{0:.2f} [#/sec] (mean)".format(options.requests / time_cost))
    print_result("Time per request",
                 "{0:.3f} [ms] (mean)".format(sum(times) / options.requests))
    print_result("Time per request",
                 "{0:.3f} [ms] (mean, across all concurrent requests)". \
                        format(time_cost*1000 / options.requests))
    print

    print "Connection Times (ms)"
    print "              min  mean[+/-sd] median   max"
    def print_row(stage, min_, mean, sd, median, max_):
        print "{stage:11} {min_:4.0f} {mean:4.0f} {sd:6.1f}  " \
                "{median:5.0f}    {max_:4.0f}". \
                format(**locals())

    min_ = min(times)
    mean = sum(times) / len(times)
    sd = math.sqrt(sum((t - mean)**2 for t in times) / (len(times) - 1)) \
            if len(times) > 1 else 0
    median = sorted(times)[len(times)/2]
    max_ = max(times)
    print_row("Total:", min_, mean, sd, median, max_)


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] service function [arg1 [arg2...]]")
    parser.add_option('-v', '--verbose', action='store_true')
    parser.add_option('-q', '--quiet', action='store_true')
    parser.add_option('--host')
    parser.add_option('--port', type='int')
    parser.add_option('-n', dest="requests", type='int', default=1,
                      help="Number of requests to perform")
    parser.add_option('-c', dest="concurrency", type='int', default=1,
                      help="Number of multiple requests to make")
    options, args = parser.parse_args()

    logging.basicConfig(
            level = options.quiet and logging.WARNING
                    or options.verbose and logging.DEBUG
                    or logging.INFO,
            format='%(asctime)s %(levelname)s %(message)s')

    service_name, function_name, args = args[0], args[1], args[2:]

    main(service_name, function_name, args, options)
