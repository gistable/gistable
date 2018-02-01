#!/usr/bin/env python

import Queue
import multiprocessing
import urllib2
import feedparser
import socket

feeds = ['http://today.reuters.com/rss/topNews',
          'http://today.reuters.com/rss/domesticNews',
          'http://today.reuters.com/rss/worldNews',
          'http://hosted.ap.org/lineups/TOPHEADS-rss_2.0.xml',
          'http://hosted.ap.org/lineups/USHEADS-rss_2.0.xml',
          'http://hosted.ap.org/lineups/WORLDHEADS-rss_2.0.xml',
          'http://hosted.ap.org/lineups/POLITICSHEADS-rss_2.0.xml',
          'http://www.nytimes.com/services/xml/rss/nyt/HomePage.xml',
          'http://www.nytimes.com/services/xml/rss/nyt/International.xml',
          'http://news.google.com/?output=rss',
          'http://feeds.salon.com/salon/news',
          'http://www.foxnews.com/xmlfeed/rss/0,4313,0,00.rss',
          'http://www.foxnews.com/xmlfeed/rss/0,4313,80,00.rss',
          'http://www.foxnews.com/xmlfeed/rss/0,4313,81,00.rss',
          'http://rss.cnn.com/rss/edition.rss',
          'http://rss.cnn.com/rss/edition_world.rss',
          'http://rss.cnn.com/rss/edition_us.rss']

# timeout for feed fetch (in seconds)
FEED_TIMEOUT = 20

def fetch_urls(work_queue, results_queue):
    '''worker function - gets feed urls from queue and parses the feed'''
    while True:
        #grab feed url from queue
        try:
            feed_url = work_queue.get(block = False)
        except Queue.Empty:
            # if queue is empty this will end the thread
            break

        # download the feed
        feed = urllib2.urlopen(feed_url, timeout = FEED_TIMEOUT).read()
        except urllib2.URLError, e:
            continue # ignore this url

        # parse the feed
        parsed_feed = feedparser.parse(feed)
        
        for e in parsed_feed.entries:
            # get the links
            if 'link' in e:
                # push them into the results queue
                results_queue.put(link)


def main():
    # create and populate the work queue with all the feed urls
    work_queue = multiprocessing.Queue()
    for feed in feeds:
        work_queue.put(feed)
    
    # create results queue for all the links extracted from the feeds
    results_queue = multiprocessing.Queue()
    
    # spawn a bunch of workers for fetch pass them the work queue & results queue
    workers = []
    for i in range(len(feeds)):
        worker = multiprocessing.Process(target=fetch_urls, args=(work_queue,results_queue,))
        worker.start()
        workers.append(worker)
 
    # wait for all the workers to finish
    for worker in workers:
        worker.join()


main()
