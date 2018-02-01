#!/usr/bin/python3
#coding: utf-8

# Download video from tvple.com

import re

import requests
import bs4


def download_file(url, filename, session=requests):
    r = session.get(url, stream=True)
    with open(filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)


def _get_data_meta(video_id, session=requests):
    url = 'http://tvple.com/%s'%(video_id,)
    r = session.get(url)
    try:
        soup = bs4.BeautifulSoup(r.text, 'lxml')
    except bs4.FeatureNotFound:
        soup = bs4.BeautifulSoup(r.text, 'html5lib')
    re_meta = re.compile(r'http://api.tvple.com/v1/player/meta\?data=')
    player_data = soup.find(True, {'data-meta': re_meta})
    if player_data is None:
        pass
    data_key = player_data['data-meta']
    return data_key.encode('ascii')


def get_video_info(video_id, session=requests):
    data_meta = _get_data_meta(video_id, session)
    r = session.get(data_meta)
    return r.json()


def get_video_url(video_id, session=requests):
    data = get_video_info(video_id, session)
    video_urls = {}
    for source in data['stream']['sources'].values():
        video_urls.update(source['urls'])
    video_url = video_urls.popitem()[1]
    return video_url


def download_video(video_id, filename, session=requests):
    video_url = get_video_url(video_id, session)
    download_file(video_url, filename, session)


if __name__ == '__main__':
    import sys
    video_ids = sys.argv[1:]
    if not video_ids:
        try:
            _input = raw_input
        except NameError:
            _input = input
        video_ids = _input('video_id: ').split()
    s = requests.Session()
    for video_id in video_ids:
        download_video(video_id, 'tvple%s.mp4'%(video_id,), s)
