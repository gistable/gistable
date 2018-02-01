# -*- coding: utf-8 -*-
'''
Usage:
    python album_fetcher.py https://plus.google.com/photos/118353143366443526186/albums/5626152497309725217
    python album_fetcher.py https://plus.google.com/118353143366443526186
    python album_fetcher.py https://plus.google.com/118353143366443526186 youremail@gmail.com yourpassword
    python album_fetcher.py https://plus.google.com/118353143366443526186 youremail@gmail.com yourpassword /out_dir/
TODO: use opt parse
'''
import os
import re
import sys
import subprocess
from collections import namedtuple
import urlparse

import urllib
import logging
import logging.handlers
import gdata.photos.service

ResultParseUrl = namedtuple('ResultParseUrl', ['user_id', 'album_id'])

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

ALBUMS_SAVE_DIR = os.path.join(PROJECT_ROOT, 'fetch_albums')

log = logging.getLogger('album_fetcher')
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-5s %(levelname)-3s %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S',
                    )


class Fetcher(object):
    def __init__(self, user_id, album_id, email=None, password=None, save_dir=None):
        self.user_id = user_id
        self.album_id = album_id
        self.email = email
        self.password = password
        self.save_dir = save_dir or ALBUMS_SAVE_DIR

    def auth(self, service):
        if self.email and self.password:
            service.email = self.email
            service.password = self.password
            service.ProgrammaticLogin()
        return service

    @staticmethod
    def parse_album_url(url):
        '''
        https://plus.google.com/photos/118353143366443526186/albums/5626152497309725217
        https://plus.google.com/114051696952559973034
        '''
        path = urlparse.urlsplit(url).path.strip('/')
        result = re.findall('photos/([\d]+)/albums/([\d]+)$', path)
        if not result:
            return ResultParseUrl(re.findall('[\d]+', path)[0], None)
        return ResultParseUrl(*result[0])

    @staticmethod
    def file_is_exists(filepath):
        if os.path.exists(filepath):
            size = os.stat(filepath).st_size
            if size:
                return True
        return False

    def get_username(self):
        return self.feed.nickname.text

    def get_albumname(self):
        return self.feed.title.text

    def get_numphotos(self):
        return self.feed.numphotos.text

    def get_output_dir(self):
        '''

        '''
        user_name = self.get_username()
        album_name = self.get_albumname()
        out_dir = os.path.join(self.save_dir, user_name, album_name)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        return out_dir

    def fetch_feed(self):
        gd_client = self.auth(gdata.photos.service.PhotosService())
        self.feed = gd_client.GetFeed(
                '/data/feed/api/user/%s/albumid/%s?kind=photo' % (self.user_id, self.album_id)
                )

        out_dir = self.get_output_dir()
        log.info("user: %s album %s in dir %s", self.get_username(), self.get_albumname(), out_dir)
        log.info("In album found %s photos", self.get_numphotos())
        for n, (filename, src_url) in enumerate(self.get_all_content_links().iteritems(), start=1):
            log.info('GET %s/%s file %s', n, self.get_numphotos(), filename)
            filepath = os.path.join(out_dir, filename)
            if self.file_is_exists(filepath):
                continue
            subprocess.call(['wget', '-q', src_url, '-O', filepath])

    def fetch(self):
        if not self.album_id:
            self.fetch_all()
        else:
            self.fetch_feed()

    def fetch_all(self):
        gd_client = gdata.photos.service.PhotosService()
        albums = gd_client.GetUserFeed(user=self.user_id)
        for album in albums.entry:
            log.info("Save album: %s, id: %s", album.title.text, album.gphoto_id.text)
            f = Fetcher(self.user_id, album_id=album.gphoto_id.text, email=self.email,
                    password=self.password, save_dir=self.save_dir)
            f.fetch_feed()

    def get_all_content_links(self):
        '''
        return: {filename:content_url}
        '''
        return dict((p.title.text, p.content.src) for p in self.feed.entry)


def main():
    args = sys.argv[1:]
    url = args[0]
    email = None
    password = None
    save_dir = ALBUMS_SAVE_DIR
    if len(args[1:]) >= 2:
        email = args[1]
        password = args[2]

    if len(args[1:]) == 1:
        save_dir = args[1]
    elif len(args[1:]) == 3:
        save_dir = args[3]

    parsed_url = Fetcher.parse_album_url(url)
    f = Fetcher(user_id=parsed_url.user_id, album_id=parsed_url.album_id,
            email=email, password=password, save_dir=save_dir)
    f.fetch()


if __name__ == '__main__':
    main()
