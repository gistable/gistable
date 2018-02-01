#!/usr/bin/env python

'''
fourdown.py

A simple script to grab links to images found on a page.

You can use as is for downloading images from thread on 4chan or you can
import FourDown and do what ever you want with it.

Usage example:

./fourdown.py http://boards.4chan.org/hr/res/1382026 /path/to/hi/res/store

'''

import os.path as op
from os import getcwd as cwd, makedirs, system
import urllib2, urllib
import re
import time
import sys


USER_AGENT = 'Mozilla/5.0 (X11; Linux i686; rv:6.0) Gecko/20100101 Firefox/6.0'
REGEX_IMAGE = 'http://images\.4chan\.org/\w+/src/\d+\.(?:png|jpeg|jpg|gif)'
WGET_PATH = '/usr/bin/wget'


class FourDown(object):

    def __init__(self, url, *args, **kwargs):
        self.url_regex = re.compile(kwargs.get('regex', REGEX_IMAGE))
        self.user_agent = re.compile(kwargs.get('user_agent', USER_AGENT))
        self.retry_delay = kwargs.get('retry_delay', 60)
        self.download_delay = kwargs.get('download_delay', 5)
        self.page_delay = kwargs.get('page_delay', 60)
        self.url = url
        self.save_to = kwargs.get('save_to', None)
        self.USE_WGET = kwargs.get('USE_WGET', False)
        self.wget_path = kwargs.get('wget_path', WGET_PATH)
        if self.save_to is None:
            self.save_to = cwd()
        else:
            self.save_to = op.abspath(self.save_to)
        self.page = ''

    def get_page(self):
        request = urllib2.Request(self.url, None, {'User-agent': self.user_agent})

        response = urllib2.urlopen(request)

        self.page = response.read()

        return self.page

    def _remove_dupes(self, items):
        # from here: http://code.activestate.com/recipes/52560/#c3
        set = {}
        return [set.setdefault(e,e) for e in items if e not in set]

    def _query_images(self):
        return self._remove_dupes(self.url_regex.findall(self.page))

    def _make_path(self):
        try:
            makedirs(self.save_to)
        except OSError:
            pass

    def _get_url(self, image, save_file):
        if self.USE_WGET:
            system('%s %s -O %s' % (self.wget_path, image, save_file))
        else:
            urllib.urlretrieve(image, save_file)

    def get_images(self):
        self._make_path()
        images = self._query_images()
        total = len(images)
        counter = 0
        print '%d images in thread' % total
        for image in images:
            counter += 1
            progress = '[%d/%d]' % (counter, total)
            filename = ''.join(image.split('/')[-1:])
            save_file = op.join(self.save_to, filename)
            if not op.isfile(save_file):
                try:
                    print '%s Getting %s...' % (progress, filename)
                    self._get_url(image, save_file)
                except Exception as error:
                    print '%s Failed getting %s, we will get it next time' % (progress, image)
                time.sleep(self.download_delay)

    def start_loop(self):
        print 'Using %s to store images' % self.save_to

        while True:
            try:
                print 'Getting page...'
                self.get_page()
            except urllib2.HTTPError as error:
                if error.code == 404:
                    print '404: Stopping...'
                    break
                else:
                    print 'Error getting page will retry in %s seconds' % self.retry_delay
                    time.sleep(self.retry_delay)
                    continue
            except urllib2.URLError:
                print 'Error getting page, will retry in %s seconds' % self.retry_delay
                time.sleep(self.retry_delay)
                continue

            print 'Downloading images...'
            self.get_images()
            print 'Done for now, will check again in %s seconds' % self.page_delay
            time.sleep(self.page_delay)


if __name__ == '__main__':

    try:
        url = sys.argv[1]
    except IndexError:
        print 'You must provide a url'
        sys.exit(1)

    try:
        save_to = sys.argv[2]
    except IndexError:
        save_to = None

    try:
        if sys.argv[3] == 'wget':
            use_wget = True
        else:
            use_wget = False
    except IndexError:
        use_wget = False

    f = FourDown(url, save_to=save_to, USE_WGET=use_wget)
    f.start_loop()
