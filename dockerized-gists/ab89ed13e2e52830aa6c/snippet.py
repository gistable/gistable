# -*- coding: utf-8 -*-
"""
common-crawl-cdx.py

A simple example program to analyze the Common Crawl index.

This is implemented as a single stream job which accesses S3 via HTTP,
so that it can be easily be run from any laptop, but it could easily be
converted to an EMR job which processed the 300 index files in parallel.

If you are only interested in a certain set of TLDs or PLDs, the program
could be enhanced to use cluster.idx to figure out the correct subset of
the 300 shards to process. e.g. the .us TLD is entirely contained in 
cdx-00298 & cdx-00299

Created on Wed Apr 22 15:05:54 2015

@author: Tom Morris <tfmorris@gmail.com>
"""

from collections import Counter
import json
import requests
import zlib


BASEURL = 'https://aws-publicdatasets.s3.amazonaws.com/'
INDEX1 = 'common-crawl/cc-index/collections/CC-MAIN-2015-11/indexes/'
INDEX2 = 'common-crawl/cc-index/collections/CC-MAIN-2015-14/indexes/'
SPLITS = 300


def process_index(index):
    total_length = 0
    total_processed = 0
    total_urls = 0
    mime_types = Counter()
    for i in range(SPLITS):
        unconsumed_text = ''
        filename = 'cdx-%05d.gz' % i
        url = BASEURL + index + filename
        response = requests.get(url, stream=True)
        length = int(response.headers['content-length'].strip())
        decompressor = zlib.decompressobj(16+zlib.MAX_WBITS)
        total = 0

        for chunk in response.iter_content(chunk_size=2048):
            total += len(chunk)
            if len(decompressor.unused_data) > 0:
                # restart decompressor if end of a chunk
                to_decompress = decompressor.unused_data + chunk
                decompressor = zlib.decompressobj(16+zlib.MAX_WBITS)
            else:
                to_decompress = decompressor.unconsumed_tail + chunk
            s = unconsumed_text + decompressor.decompress(to_decompress)
            unconsumed_text = ''

            if len(s) == 0:
                # Not sure why this happens, but doesn't seem to affect things
                print 'Decompressed nothing %2.2f%%' % (total*100.0/length),\
                    length, total, len(chunk), filename
            for l in s.split('\n'):
                pieces = l.split(' ')
                if len(pieces) < 3 or l[-1] != '}':
                    unconsumed_text = l
                else:
                    json_string = ' '.join(pieces[2:])
                    try:
                        metadata = json.loads(json_string)
                    except:
                        print 'JSON load failed: ', total, l
                        assert False
                    url = metadata['url']
                    if 'mime' in metadata:
                        mime_types[metadata['mime']] += 1
                    else:
                        mime_types['<none>'] += 1
                        # print 'No mime type for ', url
                    total_urls += 1
                    # print url
        print 'Done with ', filename
        total_length += length
        total_processed += total
    print 'Processed %2.2f %% of %d bytes (compressed).  Found %d URLs' %\
        ((total_processed * 100.0 / total_length), total_length, total_urls)
    print "Mime types:"
    for k, v in mime_types.most_common():
        print '%5d %s' % (v, k)

for index in [INDEX2]:
    print 'Processing index: ', index
    process_index(index)
    print 'Done processing index: ', index
