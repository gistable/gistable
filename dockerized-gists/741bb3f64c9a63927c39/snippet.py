#!/usr/bin/env python

import sys
import json
import mmap
import logging
import argparse

import boto
import boto.s3.connection

GIG = 2**30

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Multipart from stdin.')

    parser.add_argument('-d', '--debug',
        action='store_true',
        help='Enabled debug-level logging.',
    )

    parser.add_argument('credentials',
        type=argparse.FileType('r'),
        help='Credentials file.',
    )

    parser.add_argument('bucket')
    parser.add_argument('key')

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format='%(asctime)s %(name)-6s %(levelname)-4s %(message)s',
    )

    credentials= json.load(args.credentials)

    conn = boto.connect_s3(
        aws_access_key_id     = credentials.get('access_key'),
        aws_secret_access_key = credentials.get('secret_key'),
        host                  = credentials.get('host'),
        port                  = credentials.get('port'),
        is_secure             = credentials.get('is_secure', True),
        calling_format        = boto.s3.connection.OrdinaryCallingFormat(),
    )

    mp = conn.get_bucket(args.bucket).initiate_multipart_upload(args.key)

    i = 0
    while True:
        i += 1
        
        ramdisk = mmap.mmap(-1, GIG)
        ramdisk.write(sys.stdin.read(GIG))
        
        size = ramdisk.tell()
        if not size:
            break
        
        ramdisk.seek(0)
        logging.info('Uploading chunk {}'.format(i))
        
        try: mp.upload_part_from_file(ramdisk, part_num=i, size=size)
        except Exception as err:
            logging.error('Failed writing part - cancelling multipart.')
            mp.cancel_upload()
            raise

    logging.info('Completing multipart.')
    mp.complete_upload()