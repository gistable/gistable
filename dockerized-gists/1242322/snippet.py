#!/usr/bin/env python
#
# Only parameter is the user ID e.g. 12345678@N06, which comes
# from the last part of the URL pointing to your photostream.
#

import sys
import urllib2
import flickrapi

BUFSIZE = 32 * 1024

flickr = flickrapi.FlickrAPI('e89d78e26c44afad500037455c3bf3b6', '07c3e7adb63004e3')

(token, frob) = flickr.get_token_part_one(perms='read')
if not token:
    print 'Please authorize in your browser and press enter'
    sys.stdin.readline()                                                                                                                                                                                                                      

token = flickr.get_token_part_two((token, frob))

photos = flickr.photos_search(user_id=sys.argv[0], extras='original_format')
for p in photos[0]:
    photo = p.attrib
    link = r'''http://static.flickr.com/%s/%s_%s_o.%s''' % (photo['server'],
            photo['id'], photo['originalsecret'], photo['originalformat'])
    url = urllib2.urlopen(link)
    f = open('.'.join([photo['id'], photo['originalformat']]), 'w')

    print 'Fetching %s.%s (%s)' % (photo['id'], photo['originalformat'],
            photo['title'])
    data = url.read(BUFSIZE)
    while data:
        f.write(data)
        data = url.read(BUFSIZE)
    f.close()