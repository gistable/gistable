#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  fetch_and_combine.py
#

"""
Scans CloudFront logs in an S3 bucket for any that are new. Combines log files
into a single local file per hour. If logs for multiple CloudFront
distributions are present, combines them all.
"""

import os
import sys
import optparse
import gzip
from collections import namedtuple
from cStringIO import StringIO

import boto

CloudFrontLog = namedtuple('CloudFrontLog', 'distribution date hour hash')
LogSource = namedtuple('LogSource', 'bucket_name is_nested')

BUCKETS = [
        LogSource('some-s3-bucket-as-cloudfront-dumps-it', False),
        LogSource('some-s3-bucket-by-date', True),
    ]

# if no credentials are set here, Boto will check the environment for the
# AWS_CREDENTIAL_FILE variable and use the credentials there
AWS_ACCESS_KEY = None
AWS_SECRET_KEY = None


def fetch_new_data(log_source, dest_dir, from_prefix=None):
    "Fetch and combine logs from an S3 bucket."
    if not os.path.isdir(dest_dir):
        os.mkdir(dest_dir)

    print 'Checking logs at s3://%s' % log_source.bucket_name
    s3 = boto.connect_s3(AWS_ACCESS_KEY, AWS_SECRET_KEY)
    bucket = s3.get_bucket(log_source.bucket_name)
    store = DirectoryStore(dest_dir)

    if log_source.is_nested:
        # iterate over one level of subdirectories, e.g. dates
        def iter_keys():
            for prefix in bucket.list(delimiter='/'):
                if from_prefix and prefix.name < from_prefix:
                    continue
                for s3_key in bucket.list(prefix=prefix.name):
                    yield s3_key
    else:
        iter_keys = bucket.list

    for s3_key in iter_keys():
        if not store.is_ingested(s3_key):
            print s3_key.key
            store.ingest(s3_key)


def parse_filename(filename):
    distribution, datehour, hash_str = os.path.basename(filename).split(
            '.')[:3]
    date, hour = datehour.rsplit('-', 1)
    return CloudFrontLog(distribution, date, hour, hash_str)


class DirectoryStore(object):
    "A storage mechanism with one directory per day, one file per hour."
    def __init__(self, base_path):
        self.base_path = base_path

    def is_ingested(self, s3_key):
        log_key = parse_filename(s3_key.key)
        manifest = self._get_keyfile(log_key) + '.manifest'
        if os.path.exists(manifest):
            ingested = set(l.rstrip() for l in open(manifest))
            return os.path.basename(s3_key.key) in ingested

        return False

    def ingest(self, s3_key):
        "Ingest this file into the store."
        filename = s3_key.key
        log_key = parse_filename(filename)
        keyfile = self._get_keyfile(log_key)
        manifest = keyfile + '.manifest'

        if os.path.exists(manifest):
            ingested = set(l.rstrip() for l in open(manifest))
            if filename in ingested:
                raise Exception('already ingested: %s' % filename)

        # fetch the data
        s3_key.open_read()
        gzdata = s3_key.read()
        data = gzip.GzipFile(fileobj=StringIO(gzdata)).read()

        # store it and record the manifest
        parent_dir = os.path.dirname(keyfile)
        if not os.path.isdir(parent_dir):
            os.mkdir(parent_dir)

        with gzip.open(keyfile + '.gz', 'a') as ostream:
            ostream.write(data)

        with open(manifest, 'a') as ostream:
            print >> ostream, os.path.basename(filename)

    def _get_keyfile(self, log_key):
        return os.path.join(self.base_path, log_key.date, log_key.hour)


def _create_option_parser():
    usage = \
"""%prog [options] dest_dir

Update a directory cache with new snowplow logs."""

    parser = optparse.OptionParser(usage)
    parser.add_option('--from', action='store', dest='from_prefix',
            help='Skip until this prefix.')

    return parser


def main(argv):
    parser = _create_option_parser()
    (options, args) = parser.parse_args(argv)

    if len(args) != 1:
        parser.print_help()
        sys.exit(1)

    dest_dir, = args
    print 'FETCHING SNOWPLOW LOGS'
    for log_source in BUCKETS:
        fetch_new_data(log_source, dest_dir, from_prefix=options.from_prefix)
    print


if __name__ == '__main__':
    main(sys.argv[1:])
