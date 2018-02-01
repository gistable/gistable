#!/usr/bin/env python
# -*- coding:utf-8 -*-
import urllib2
from bs4 import BeautifulSoup
import requests

BASEURL = 'http://www.songtaste.com/time.php'

def get_song_url(url):
    html = urllib2.urlopen(url).read()
    soup = BeautifulSoup(html)
    data = soup.select('#playicon > div > a')[0]['href']
    song_str = data.split(';')[0].split(':')[1].split(',')[2].split('\'')[1]
    song_id = url.split('/')[-2]
    payload = {'str': song_str, 'sid': song_id, 't': 0}
    r = requests.post(BASEURL, data=payload)
    song_url = r.text
    return song_url


def get_song_data(url):

    url = get_song_url(url)
    song = urllib2.urlopen(url)
    print song

if __name__ == '__main__':
    get_song_data('http://www.songtaste.com/song/3467134/')