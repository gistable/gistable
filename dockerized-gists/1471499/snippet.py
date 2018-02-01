#!/usr/bin/env python

import gevent.monkey
gevent.monkey.patch_all()

import boto
import config
import gevent
import gevent.pool
import os
import sys
import time
import traceback
import optparse

from cStringIO import StringIO

CHUNK_SIZE = 5 * 1024 * 1024

def get_connection():
    return boto.connect_s3(aws_access_key_id = config.aws['aws_access_key_id'], aws_secret_access_key = config.aws['aws_secret_access_key'])

def upload_part(mp, fname, idx, offset):
    f = open(fname)
    f.seek(offset)
    content = f.read(CHUNK_SIZE)
    f.close()

    success = False
    for x in xrange(3):
        try:
            conn = get_connection()
            bucket = conn.lookup(mp.bucket_name)

            p = boto.s3.multipart.MultiPartUpload(bucket)
            p.id = mp.id
            p.key_name = mp.key_name

            p.upload_part_from_file(StringIO(content), idx+1, replace=True)
            success = True
            break
        except Exception, e:
            print "Error in part upload - %s %s %s" % (fname, idx, offset)
            print traceback.format_exc()

    assert success, "Part failed - %s %s %s" % (fname, idx, offset)

def upload(options):
    conn = get_connection()
    bck = conn.create_bucket(options.bucket)

    pool = gevent.pool.Pool(options.concurrency)

    for fname in options.files:
        if options.path == '.':
            fpath = os.path.basename(fname)
        else:
            fpath = os.path.join(options.path, os.path.basename(fname))

        s = "Putting: %s -> %s/%s ..." % (fname, options.bucket, fpath),
        print "%-80s" % (s),
        sys.stdout.flush()

        start = time.time()

        size = os.stat(fname).st_size
        if size > (CHUNK_SIZE*2) and options.concurrency > 1:
            mp = bck.initiate_multipart_upload(fpath, reduced_redundancy=options.reduced_redundancy)

            greenlets = []
            idx = offset = 0
            while offset < size:
                greenlets.append( pool.spawn(upload_part, mp, fname, idx, offset) )
                idx += 1
                offset += CHUNK_SIZE

            gevent.joinall(greenlets)
            cmp = mp.complete_upload()
        else:
            key = bck.new_key(fpath)
            f = open(fname)
            key.set_contents_from_file(f, reduced_redundancy=options.reduced_redundancy, replace=True)
            f.close()

        size = float(size)/1024/1024
        elapsed = time.time() - start

        print " %6.1f MiB in %.1fs (%d KiB/s)" % (size, elapsed, int(size*1000/elapsed))

def main(argv):
    parser = optparse.OptionParser()
    parser.set_usage('%prog [options] <bucket> <path> <files>')
    parser.add_option('-c', '--concurrency', dest='concurrency', type='int', help='Number of parts to upload simultaneously', default=3)
    parser.add_option('-r', '--reduced_redundancy', dest='reduced_redundancy', help='Use S3 reduced redundancy', action='store_true', default=False)

    options, args = parser.parse_args()
    if not args or len(args) < 3:
        parser.print_help()
        sys.exit(1)

    options.bucket = args[0]
    options.path = args[1]
    options.files = args[2:]

    upload(options)

if __name__ == '__main__':
    main(sys.argv)
