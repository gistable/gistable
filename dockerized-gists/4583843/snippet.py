#!/usr/bin/env python

import tweepy
from BeautifulSoup import BeautifulSoup as parser
import urllib
import sys


import argparse
import ConfigParser
import os

def detect_feeds_in_HTML(input_stream):
    """ examines an open text stream with HTML for referenced feeds.

    This is achieved by detecting all ``link`` tags that reference a feed in HTML.

    :param input_stream: an arbitrary opened input stream that has a :func:`read` method.
    :type input_stream: an input stream (e.g. open file or URL)
    :return: a list of tuples ``(url, feed_type)``
    :rtype: ``list(tuple(str, str))``
    """
    # check if really an input stream
    if not hasattr(input_stream, "read"):
        raise TypeError("An opened input *stream* should be given, was %s instead!" % type(input_stream))
    result = []

    # get the textual data (the HTML) from the input stream
    html = parser(input_stream.read())

    # find all links that have an "alternate" attribute
    feed_urls = html.findAll("link", rel="alternate")

    # extract URL and type
    for feed_link in feed_urls:
        url = feed_link.get("href", None)
        # if a valid URL is there
        if url:
            result.append(url)
    return result

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def process_feeds(tuples, user):
   """ Take tuples from detect_feeds_in_HTML() and create an outline entry for opml
   """
   for t in tuples:
       html = parser(user.url, convertEntities=parser.HTML_ENTITIES).contents[0]

       # Ignore feeds for comments
       if "comment" in t:
           next

       # Ignore annoying typo in the html from a friend
       if "\"" in t:
           next

       # Convert relative URLs
       if "http" in t:
           xml = parser(t, convertEntities=parser.HTML_ENTITIES).contents[0]
       else:
           myxml = html + t
           xml = parser(myxml, convertEntities=parser.HTML_ENTITIES).contents[0]

       # If we've got something, rather than nothing, return a hash
       if xml:
           return {'title': user.name, 'html_url': html, 'xml_url': xml}
       else:
           return None

def find_feed(user):
   """ Takes a twitter api User object, grabs URL and then searches for feeds
   """
   if user.url:
       try:
           site = urllib.urlopen(user.url)
           feed = process_feeds(detect_feeds_in_HTML(site), user)
           return feed

       except Exception, err:
            sys.stderr.write('ERROR: %(err)s in %(url)s\n' % {'err': str(err), 'url': user.url})
            pass
   else:
        return None

def connect_api(args):
    auth = tweepy.OAuthHandler(args.consumer_key, args.consumer_secret)
    auth.set_access_token(args.access_token, args.access_token_secret)

    api = tweepy.API(auth)
    return api

def extract_entity_urls(user):
    urls = []
    print user.__getstate__()
    try:
        if user.entities.url.urls:
            for u in user.entities.url.urls:
                urls.append(u.url)
    except:
        return urls
    return urls

def get_users(api, args):

    if args.followers:
        users = api.followers_ids()

    if args.friends:
        users = api.friends_ids()

    return users

def get_feeds(api, users, args):
    feeds = []
    # TODO put these in a database
    # Need to associate with a user
    for c in chunks(users, args.chunks):
        users = api.lookup_users(c)
        feeds = [find_feed(u) for u in users]
    return feeds

def get_feeds_from_entities(api, users, args):
    entity_urls = []
    for c in chunks(users, args.chunks):
        users = api.lookup_users(c)
        entities = [url for u in users for url in extract_entity_urls(u)]
    return entities

def print_opml(api, args):

    users = get_users(api, args)

    # truncate users to our stopafter point if specified
    if args.stop_after:
        users = users[1:args.stop_after]

    feeds = get_feeds(api, users, args)
    #feeds = get_feeds_from_entities(api, users, args)

    if args.output:
        sys.stdout = open(args.output, 'w')

    opml_start = """<?xml version="1.0" encoding="UTF-8"?>
    <opml version="1.1">
    <head>
    <title>People who follow me</title>
    </head>
    <body>
    <outline text="People who follow me" title="People who follow me">"""

    opml_end = """</outline>
    </body>
    </opml>"""

    print opml_start

    opml_outline_feed = '<outline text="%(title)s" title="%(title)s" type="rss" version="RSS" htmlUrl="%(html_url)s" xmlUrl="%(xml_url)s" />'
    # Do this lookup in chunks of 100 because of twitter API limitations
    # Loop over URLS
    for f in feeds:
        if f:
            print opml_outline_feed % f

    print opml_end

if __name__ == '__main__':

    conf_parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter, add_help=False)
    conf_parser.add_argument("--config", dest="filename", help="Config File input", metavar="FILE", default=None)
    args, remaining_argv = conf_parser.parse_known_args()

    if args.filename:
        config = ConfigParser.SafeConfigParser()
        config.read([args.filename])
        defaults = dict(config.items("Defaults"))
    else:
        defaults = { "option":"default" }

    argparser = argparse.ArgumentParser(parents=[conf_parser])
    argparser.add_argument("--followers", help="fetch follower ids and urls", action="store_true", default=False)
    argparser.add_argument("--friends", help="fetch friend ids and urls", action="store_true", default=False)
    argparser.add_argument("--output", help="file to write output to", action="store", default=None)
    argparser.add_argument("--consumer_key", help="Consumer key (app dev)", action="store", default=None)
    argparser.add_argument("--consumer_secret", help="Consumer secret (app dev)", action="store", default=None)
    argparser.add_argument("--access_token", help="Twitter access token", action="store", default=None)
    argparser.add_argument("--access_token_secret", help="Twitter access token secret for user", action="store", default=None)
    argparser.add_argument("--chunks", help="chunks of users to query", action="store", default=100, type=int)
    argparser.add_argument("--stop-after", help="number of users to stop after", action="store", default=None, type=int)
    argparser.set_defaults(**defaults)
    args = argparser.parse_args(remaining_argv)
    api = connect_api(args)
    print_opml(api, args)