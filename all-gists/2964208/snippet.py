#!/usr/bin/env python                                                                                                                                                                                                                                                                                                       

"""                                                                                                                                                                                                                                                                                                                         
                                                                                                                                                                                                                                                                                                                            
Proof of concept scraper for pinnacle sports                                                                                                                                                                                                                                                                                
                                                                                                                                                                                                                                                                                                                            
"""

FEED = "http://xml.pinnaclesports.com/pinnacleFeed.aspx"

import lxml.etree
import os
import sys
import time
import urllib2



def recursive_dict(element):
    return element.tag, dict(map(recursive_dict, element)) or element.text


def downloadtree(feed_url, last_game=None, last_contest=None, feed_time=None):
    """ kwargs are for future use """
    request_url = feed_url
    if feed_time is not None:
        request_url += "?last=%s" % feed_time
    
    request = urllib2.Request(request_url)
    
    t0 = time.time()
    response = urllib2.urlopen(request).read()
    t1 = time.time()
    
    sys.stderr.write("Read feed in %s seconds\n" % (t1 - t0))
    
    tree = lxml.etree.fromstring(response)
    
    return tree


def timings_and_events(tree):
    if not isinstance(tree, lxml.etree._Element):
        tree = tree.getroot()
    root_elements = [e for e in tree]
    feed_time, last_contest, last_game = \
        [element.text for element in root_elements[:-1]]
    event_elements = root_elements[-1].iterchildren()
    events = map(recursive_dict, event_elements)
    return feed_time, last_contest, last_game, events


def all_events(tree):
    return (recursive_dict(e)[1] for e in tree.iterfind("//event"))


def live_events(events):
    return [e for label, e in events if "IsLive" not in e or e["IsLive"] != "No"]



if __name__ == "__main__":
    tree = downloadtree(FEED)
    feed_time, last_contest, last_game, events = timings_and_events(tree)
    print "there are %s live events" % liveevents(events)

    time.sleep(60)

    new_tree = downloadtree(FEED, feed_time=feed_time)
    feed_time, last_contest, last_game, new_events = timings_and_events(new_tree)
    print "%s more events came in" % len(new_events)
