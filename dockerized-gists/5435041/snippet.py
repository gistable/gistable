#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import urllib
from time import sleep
import pytumblr  # https://github.com/tumblr/pytumblr

# set yours:
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
OAUTH_TOKEN = ''
OAUTH_TOKEN_SECRET = ''

def download_img(url, dst=os.getcwd()):
    dst = os.path.join(dst, os.path.basename(url))

    if not os.path.exists(dst):
        urllib.urlretrieve(url, dst)
        print >>sys.stderr, 'downloaded:', url


def _main():
    client = pytumblr.TumblrRestClient(CONSUMER_KEY,
                                       CONSUMER_SECRET,
                                       OAUTH_TOKEN,
                                       OAUTH_TOKEN_SECRET)
    params = {'offset': 0, 'limit': 20}

    while True:
        likes = client.likes(**params)

        for post in likes['liked_posts']:
            photos = post.get('photos')
            
            if photos:
                for photo in photos:
                    orig = photo.get('original_size')
                    if orig:
                        download_img(orig.get('url'))

        params['offset'] += 20
        params['limit'] += 20
        if params['limit'] > likes['liked_count']:
            break

        sleep(1)
        
if __name__ == '__main__':
    _main()
