#!/usr/bin/env python
"""
This script can be used to get a per-author RSS feed on iMore.com.  It will try to
cache the entries, so the last 40 entries from an author will show up, even if
they're no longer in the main feed.

To invoke, just call this script at the command line:

    python settern_rss.py
  
and the new feed should be written to settern.xml.

Made after seeing @tflight's tweet: https://twitter.com/tflight/status/698569279554228224
"""

import collections
from datetime import datetime
import json
import re
import urllib2


# Configuration options
AUTHOR = 'Serenity Caldwell'
OUTFILE = 'settern.xml'
MAX_POSTS = 40

# URL for the iMore master feed
RSS_FEED = 'http://www.imore.com/rss.xml'


# We have to use a non-greedy regex, or the first item will
# match the entire feed.
#
# Yes, using regular expressions is a terrible way to parse XML files,
# but I'm making simple modifications and it preserves most of the
# iMore RSS stuff.
ITEM_REGEX = re.compile('(<item>.*?</item>)')
CREATOR_REGEX = re.compile('<dc:creator>(.*?)</dc:creator>')
PUBDATE_REGEX = re.compile('<pubDate>(.*?)</pubDate>')
GUID_REGEX = re.compile('<guid isPerma[lL]ink="false">([\d]*) at http://www.imore.com</guid>')


# Read the iMore master feed
rss_feed = urllib2.urlopen(RSS_FEED).read()

# All the posts are <item> entries in the RSS feed, and come as a
# single contiguous block.
items = ITEM_REGEX.findall(rss_feed)
item_string = ''.join(items)

# Filter out all the posts that aren't written by @settern
author_items = []
for item in items:
    creator = CREATOR_REGEX.findall(item).pop()
    if creator == AUTHOR:
        author_items.append(item)

# We may not have enough posts to fill the feed.  Look in entries.json
# for other items by this author -- these are the cached entries.
if len(author_items) < MAX_POSTS:
    try:
        with open('entries.json') as cache:
            cached_entries = json.loads(cache.read())
    except (IOError, OSError, ValueError):
        cached_entries = {}

# Add the cached entries to the items served from the live feed.
author_items.extend(cached_entries.get(AUTHOR, []))

# Now we need to remove duplicate items, and get the most recent posts
Item = collections.namedtuple('Item', ['pubDate', 'text'])
guid_items = {}
for item in author_items:
    guid = GUID_REGEX.findall(item).pop()

    # Only write an item if it's not already there: that way posts from
    # the live feed take precedence
    if guid not in guid_items:
        pubdate = PUBDATE_REGEX.findall(item).pop()
        date_str = str(datetime.strptime(pubdate, '%a, %d %b %Y %H:%M:%S GMT'))
        guid_items[guid] = Item(date_str, item)

# Now we have a list of (in theory) de-duplicated RSS items.  Sort them
# in reverse order, so newest posts come first.
dated_items = list(guid_items.values())
dated_items = [i.text for i in reversed(sorted(dated_items))]

# Get only the MAX_POSTS most recent posts
items_to_use = dated_items[:MAX_POSTS]

# Write these back to the cache
cached_entries[AUTHOR] = items_to_use
out_json = json.dumps(cached_entries)
with open('entries.json', 'w') as cache:
    cache.write(out_json)

# Drop the items_to_use into the XML string to make an RSS feed version
# with only these posts.
items_to_use_string = ''.join(items_to_use)
new_rss_feed = rss_feed.replace(item_string, items_to_use_string)
with open(OUTFILE, 'w') as outfile:
    outfile.write(new_rss_feed)
