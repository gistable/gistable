#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Instapusher. Push images from a directory automatically to Instagram.

# Schedule script with cron eg:

# 0 18 * * * /path/to/instapusher --login <your_username> \
#            --password <your_password> --random-delay 30 <dir>

# Give working directory in form /path/to/dir
# The directory structure contains two subdirs and they should contain presized
# 1080x1080px jpg-files:
# directory/todo  <- contains jpg images to send randomly by this script
# directory/sent  <- images that have been sent are moved here

# Example file listing
# /Users/you/instapush-dir/sent/possible bugfix #coding.jpg
# /Users/you/instapush-dir/sent/this one too #stackoverflow.jpg
# /Users/you/instapush-dir/todo/this pic is going to change the world.jpg


import requests
import hmac
import random
import uuid
import urllib
import json
import hashlib
import time
import argparse

from random import randint
from time import sleep

from os import listdir
from os.path import isfile, join
from shutil import move


try:
    # python 2
    urllib_quote_plus = urllib.quote
except:
    # python 3
    urllib_quote_plus = urllib.parse.quote_plus


def _generate_signature(data):
    return hmac.new('b4a23f5e39b5929e0666ac5de94c89d1618a2916'.encode('utf-8'),
                    data.encode('utf-8'), hashlib.sha256).hexdigest()


def _generate_user_agent():
    resolutions = ['720x1280', '320x480', '480x800', '1024x768', '1280x720',
                   '768x1024', '480x320']
    versions = ['GT-N7000', 'SM-N9000', 'GT-I9220', 'GT-I9100']
    dpis = ['120', '160', '320', '240']

    ver = random.choice(versions)
    dpi = random.choice(dpis)
    res = random.choice(resolutions)

    return (
        'Instagram 4.{}.{} '
        'Android ({}/{}.{}.{}; {}; {}; samsung; {}; {}; smdkc210; en_US)'
    ).format(
        random.randint(1, 2),
        random.randint(0, 2),
        random.randint(10, 11),
        random.randint(1, 3),
        random.randint(3, 5),
        random.randint(0, 5),
        dpi, res, ver, ver,)


class InstagramSession(object):

    def __init__(self):
        self.guid = str(uuid.uuid1())
        self.device_id = 'android-{}'.format(self.guid)
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': _generate_user_agent()})

    def login(self, username, password):

        data = json.dumps({
            "device_id": self.device_id,
            "guid": self.guid,
            "username": username,
            "password": password,
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        })
        print(data)

        sig = _generate_signature(data)

        payload = 'signed_body={}.{}&ig_sig_key_version=4'.format(
            sig,
            urllib_quote_plus(data)
        )

        r = self.session.post("https://instagram.com/api/v1/accounts/login/",
                              payload)
        r_json = r.json()
        print(r_json)

        if r_json.get('status') != "ok":
            return False

        return True

    def upload_photo(self, filename):
        data = {
            "device_timestamp": time.time(),
        }
        files = {
            "photo": open(filename, 'rb'),
        }

        r = self.session.post("https://instagram.com/api/v1/media/upload/",
                              data, files=files)
        r_json = r.json()
        print(r_json)

        return r_json.get('media_id')

    def configure_photo(self, media_id, caption):
        data = json.dumps({
            "device_id": self.device_id,
            "guid": self.guid,
            "media_id": media_id,
            "caption": caption,
            "device_timestamp": time.time(),
            "source_type": "5",
            "filter_type": "0",
            "extra": "{}",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        })
        print(data)

        sig = _generate_signature(data)

        payload = 'signed_body={}.{}&ig_sig_key_version=4'.format(
            sig,
            urllib_quote_plus(data)
        )

        r = self.session.post("https://instagram.com/api/v1/media/configure/",
                              payload)
        r_json = r.json()
        print(r_json)

        if r_json.get('status') != "ok":
            return False

        return True


def select_img(path):
    '''Select a random jpg image file from given path'''
    print(path)
    jpg_files = [f for f in listdir(path)
                 if isfile(join(path, f)) and '.jpg' in f]
    print("Found %s jpg files." % len(jpg_files))

    filecount = len(jpg_files)
    if filecount == 0:
        raise ValueError('No jpg files found!')

    if filecount > 1:
        idx = randint(0, filecount - 1)
    else:
        idx = 0

    return jpg_files[idx]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', help='Base directory')
    parser.add_argument('--login', help='Instagram login', required=True)
    parser.add_argument('--password', help='Instagram password', required=True)
    parser.add_argument('--random_delay', help='Random delay in minutes')

    # parser.add_argument('--comment', '-c',
    #                     help='Short comment can be posted right from here')
    # parser.add_argument('--long-comment', '-C',
    #                     help='File with utf-8 long comment')
    return parser.parse_args()


def main(args):
    if args.random_delay:
        rand_mins = randint(0, int(args.random_delay))
        sleep_time = 60 * rand_mins
        print("sleeping for %s minutes.." % rand_mins)
        sleep(sleep_time)

    img_file = select_img(args.directory + '/todo/')
    comment = img_file[:-4]

    img_path = args.directory + '/todo/' + img_file

    insta = InstagramSession()
    if insta.login(args.login, args.password):
        print 'Logged in as %s' % args.login
        media_id = insta.upload_photo(img_path)
        print media_id
        if media_id is not None:
            if len(comment) > 0:
                insta.configure_photo(media_id, comment)
                move(img_path, args.directory + '/sent/')
    print 'Done'


if __name__ == "__main__":
    main(parse_args())
