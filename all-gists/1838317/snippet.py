#!/usr/bin/python
#
# Get Cloudwatch metrics for an ELB
#
# Inspired by http://onemoredigit.com/post/3263274796/single-instance-cloudwatch-stats-with-boto
#

import datetime
import sys

from boto.exception import BotoServerError
import boto


class InstanceDimension(dict):
    """
    Helper class for get_metric_statistics call
    """
    def __init__(self, name, value):
        self[name] = value


def get_elb_stats(name, metric, minutes=60, period=60):
    """
    Get CloudWatch statistics for a load balancer


    API docs: http://docs.amazonwebservices.com/AmazonCloudWatch/latest/APIReference/API_GetMetricStatistics.html

    Hint: to figure out the exact params, use the AWS console and look
    at the query params when clicking on cloudwatch metrics...

    @param name: string, ELB name
    @param metric: string, metric to retrieve (RequestCount, HTTPCode_Backend_2XX, etc)
    @param minutes: int, minutes to look back
    @param period: int, sample bucket size in seconds
    """

    print 'Stats for \'%s\' for the last %dm (bucket: %ds):' % (name, minutes, period)
    try:
        c = boto.connect_cloudwatch()
        end = datetime.datetime.utcnow()
        start = end - datetime.timedelta(minutes=minutes)
        stats = c.get_metric_statistics(period, start, end, metric,
                                        'AWS/ELB', 'Sum',
                                        InstanceDimension("LoadBalancerName", name)
        )
        for stat in stats:
            print '\t%s: %f' % (stat[u'Timestamp'], stat[u'Sum'])

    except BotoServerError, error:
        print >> sys.stderr, 'Boto API error: ', error


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print >> sys.stderr, 'Usage: %s <ELB name>' % sys.argv[0]
        sys.exit(1)

    get_elb_stats(sys.argv[1], 'RequestCount', 1, 60)
    get_elb_stats(sys.argv[1], 'RequestCount', 5, 60)
    get_elb_stats(sys.argv[1], 'RequestCount', 5, 300)
    get_elb_stats(sys.argv[1], 'RequestCount', 60, 60)
    get_elb_stats(sys.argv[1], 'RequestCount', 60, 300)
    get_elb_stats(sys.argv[1], 'RequestCount', 60, 3600)
