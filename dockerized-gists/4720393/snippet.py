# -*- coding: utf-8 -*-

"""
Simple program for invalidating paths in a CloudFront distribution.

The AWS web console allows you to do this if you know the paths,
but sometimes you've got to find the paths from your database or some
other means that's too burdensome to copy/paste into a web form.

To run...

$ mkvirtualenv cloudfrontinvalidate
$ workon cloudfrontinvalidate
$ pip install boto
$ python cloudfront_invalidate.py dry_run

"""

import sys
import boto

AWS_KEY = '[AWS KEY HERE]'
AWS_SECRET = '[AWS SECRET HERE]'
DISTRIBUTION_ID = '[DISTRIBUTION ID HERE]'

def invalidate_paths(dry_run=False):
    paths = _get_paths()
    num_paths = len(paths)
    if num_paths > 0:
        cloudfront = boto.connect_cloudfront(AWS_KEY, AWS_SECRET)
        # Can only do 1000 invalidates at a time, so send them in chunks
        # Note: 1st 1000 invalidations per month are free, anything over
        # that costs $$$
        chunk_begin = 0
        chunk_end = min(num_paths, 1000)
        while chunk_begin < num_paths:
            paths_chunk = paths[chunk_begin:chunk_end]
            if dry_run:
                print "Would've created an invalidation request."
            else:
                req = cloudfront.create_invalidation_request(DISTRIBUTION_ID, paths_chunk)
                print "Created invalidation request."

            chunk_begin = chunk_end
            chunk_end = min(chunk_end + 1000, num_paths)

    if dry_run:
        print "Without the dry_run arg, would've invalidated {0} paths.".format(num_paths)
    else:
        print "Invalidated {0} paths.".format(num_paths)

def _get_paths():
    """Gets the CloudFront paths to invalidate. """
    # This part is left to your particular use case
    # For me, I had to write some DB queries to find
    # the specific file paths I wanted to invalidate.
    return []

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'dry_run':
            invalidate_paths(dry_run=True)
        else:
            print 'Invalid command. For a dry run: python cloudfront_invalidate.py dry_run'
    else:
        invalidate_paths()

    sys.exit()



