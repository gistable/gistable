#!/usr/bin/env python

# I got the meat of this script from somewhere but I can't remember where...
# if it was yours, let me know and I'll give credit.

'''
download macsysadmin videos

requires:

pip install requests
pip install beautifulsoup4
'''

import os
import sys

import requests
from bs4 import BeautifulSoup, SoupStrainer

year = '2015'
url = 'http://docs.macsysadmin.se/%s/%sdoc.html' % (year, year)
output_dir = 'macsysadmin%s' % year

def get_videos(url):
    '''Returns a list of video links'''
    req = requests.get(url)
    soup = BeautifulSoup(req.content, parse_only=SoupStrainer('a', href=True))
    return [link.attrs['href'] for link in soup if 'mp4' in link.attrs['href']]

def save_videos(urls, dir_name):
    '''Saves videos to specified directory'''
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    for url in urls:
        print 'Downloading %s' % url
        req = requests.get(url, stream=True)
        output_file = dir_name + '/' + url.split('/')[-1]
        with open(output_file, 'w') as f:
            for chunk in req.iter_content(chunk_size=3000):
                f.write(chunk)

def main():
    videos = get_videos(url)
    save_videos(videos, output_dir)
    
if __name__ == '__main__':
    main()