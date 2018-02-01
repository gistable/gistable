# Hacky script for downloading videos from PyVideo and converting them to m4v 
# format so they can be synced onto your apple device.  Useful if you
# want to see everything that happened at PyCon while commuting.
# 
# Requirements:
# * pip install requests BeautifulSoup
# * youtube-dl (from https://github.com/rg3/youtube-dl/) - add this to the 
#   directory where this script runs and ensure its execute bit is set.  
#   This was the only YouTube downloader I found that worked.  It doesn't 
#   really have a good Python API so I call it through os.system.
# * ffmpeg (use brew install --use-gcc ffmpeg) - used to convert from .flv to
#   .m4v
#
# Usage:
# 
# 1. Fetch the videos you want and convert them:
#    $ python fetch_pyvideos.py
# 
# 2. Choose which videos you want to download
# 
# 3. Import them into iTunes using 'File' > 'Add to Library'

import requests
from BeautifulSoup import BeautifulSoup as Soup
from urlparse import urlparse
import os

def fetch_youtube_urls(category_url):
    # Scrape the pyvideo site to get titles and descriptions of 
    # each video so you can choose which you want to download.
    urls = []
    soup = Soup(requests.get(category_url).content)
    for div in soup('div', attrs={'class': 'row-fluid section'}):
        title = div.findAll('a')[1].text
        description = div.findNext('div', attrs={'class':
                                                 'span7'}).findNext('p').text
        os.system('clear')
        print
        print title
        print '=' * len(title)
        print description
        print
        result = raw_input('Fetch this video? [y/N] ' )
        if result.lower() != 'y':
            continue

        video_path = div.findNext('a')['href']
        video_url = 'http://pyvideo.org%s' % video_path
        video_soup = Soup(requests.get(video_url).content)
        youtube_url = video_soup('embed')[0]['src']
        urls.append(youtube_url)
    return urls

def download_video(url):
    # Use youtube-dl to handle the download
    os.system('./youtube-dl "%s"' % url)
    # youtube-dl will download the video to a file with
    # name matching the YouTube ID of the video.
    parts = urlparse(url)
    id = parts.path.split('/')[2].split('&')[0]
    return '%s.flv' % id

def convert_flv_to_m4v(flv_path, m4v_path):
    # Shell out to ffmpeg to do the conversion - hide the 
    # output as there's masses of it.
    os.system('ffmpeg -i %s %s > /dev/null' % (flv_path, m4v_path))

def notify(msg):
    line = '-' * len(msg)
    print "\n%s\n%s\n%s\n\n" % (line, msg, line)

if __name__ == '__main__':
    # Insert category page URL here
    pyvid_url = 'http://pyvideo.org/category/17/pycon-us-2012'

    # Ensure we have a local folder to download to
    foldername = 'quicktime'
    if not os.path.exists(foldername):
        os.mkdir(foldername)

    notify('Fetching video URLs from %s' % pyvid_url)
    for url in fetch_youtube_urls(pyvid_url):
        notify('Downloading %s' % url)
        flv_filename = download_video(url)
        m4v_filepath = '%s/%s.m4v' % (foldername, flv_filename.split('.')[0])
        notify('Converting %s tp M4V format %s' % (flv_filename, m4v_filepath))
        convert_flv_to_m4v(flv_filename, m4v_filepath)
    notify('Video fetching complete')