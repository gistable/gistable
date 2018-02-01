#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from boto.s3.connection import S3Connection
from cStringIO import StringIO
from PIL import Image as pil

AWS_KEY = '[AWS KEY HERE]'
AWS_SECRET = '[AWS SECRET HERE]'
BUCKET_NAME = '[BUCKET NAME]'

def start_compressing(dry_run=False):
    conn = S3Connection(AWS_KEY, AWS_SECRET)
    bucket = conn.get_bucket(BUCKET_NAME)

    i = 0
    for img in bucket.list():
        if img.size > 500000:
            if not dry_run:
                compress_image(img, i)
            i += 1

    if dry_run:
        print 'Will compress {0} images'.format(i)
    else:
        print 'Compressed {0} images'.format(i)


def compress_image(pic, index):
    print u'{0}: compressing image: {1}'.format(index, pic.name)
    input_file = StringIO(pic.get_contents_as_string())
    img = pil.open(input_file)
    tmp = StringIO()
    img.save(tmp, 'JPEG', quality=80)
    tmp.seek(0)
    output_data = tmp.getvalue()

    headers = dict()
    headers['Content-Type'] = 'image/jpeg'
    headers['Content-Length'] = str(len(output_data))
    pic.set_contents_from_string(output_data, headers=headers, policy='public-read')
    
    tmp.close()
    input_file.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'dry_run':
            start_compressing(dry_run=True)
        else:
            print 'Invalid command. For a dry run please run: python compress_s3_images.py dry_run'
    else:
        start_compressing()
    sys.exit()