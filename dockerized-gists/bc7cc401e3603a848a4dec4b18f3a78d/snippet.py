#!/usr/bin/env python
"""
Warm the caches of your website by crawling each page defined in sitemap.xml.
To use, download this file and make it executable. Then run:
./cache-warmer.py --threads 4 --file /data/web/public/sitemap.xml -v
"""
import argparse
import multiprocessing.pool as mpool
import os.path
import re
import sys
import time
import requests
import subprocess


results = []
start = time.time()


def parse_options():
    parser = argparse.ArgumentParser(description="""Cache crawler based on a sitemap.xml file""")
    parser.add_argument('-t', '--threads', help='How many threads to use', default=10, required=False, type=int)
    parser.add_argument('-f', '--file', help='The sitemap xml file', required=True, type=str)
    parser.add_argument('-v', '--verbose', help='Be more verbose', action='store_true', default=False)

    args = parser.parse_args()
    if not os.path.isfile(args.file):
        parser.error('Could not find sitemap file %s' % args.file)
    return args


def crawl_url(url, verbose=False):
    if verbose:
        print "Crawling {}".format(url)
    a = requests.get(url, headers={"user-agent": "SitemapCacheWarmer"})
    return {'exit': 0 if a.ok() else 1, 'out': a.text, 'url': url}


def make_results():
    errcount = 0
    exec_time = format(time.time() - start, '.4f')
    for item in results:
        if item['exit'] == 0:
            continue
        else:
            errcount += 1
            print "Errors detected in %s:\n%s\n" % (item['url'], item['out'])
            print "=" * 50
    if errcount == 0:
        print "All DONE! - All urls are warmed! - done in %s " % exec_time
        return 0
    else:
        print "%d Errors detected! - done in %ss" % (errcount, exec_time)
        return 1


def get_sitemap_urls(filename):
    with open(filename) as fh:
        return re.findall('<loc>(.*?)</loc>?', fh.read())


def callback(output):
    results.append(output)


def main():
    args = parse_options()
    sitemap_urls = get_sitemap_urls(args.file)

    if args.verbose:
        print "Crawling {} urls with {} threads\n[Please Wait!]".format(len(sitemap_urls), args.threads)
        print "=" * 50

    pool = mpool.ThreadPool(args.threads)
    for url in sitemap_urls:
        pool.apply_async(crawl_url, args=(url,), callback=callback)
    pool.close()
    pool.join()
    sys.exit(make_results())      


if __name__ == "__main__":
    main()