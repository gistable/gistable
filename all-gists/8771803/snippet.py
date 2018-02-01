#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import codecs
import getpass
import glob
import json
import logging
import lxml.etree
import os
import requests
import time


logger = logging.getLogger()


def _method(name):
    url = 'https://api.juick.com/' + name

    def method_impl(self, **kwargs):
        MAX_RETRIES = 5
        TIMEOUT = 1

        for retry in xrange(MAX_RETRIES):
            logger.info('Juick.%s%r', name, kwargs)
            r = self._session.get(url, params=kwargs)
            logger.debug('Juick.%s%r -> %s %s',
                         name, kwargs, r.status_code, r.reason)

            if r.status_code // 100 != 5:
                break

            logger.info('[%d / %d] Got %s %s, retrying in %ss...',
                        retry + 1, MAX_RETRIES,
                        r.status_code, r.reason, TIMEOUT)
            time.sleep(TIMEOUT)

        r.raise_for_status()
        return r.json()
    return method_impl


class Juick(object):
    def __init__(self, auth=None):
        self._session = requests.Session()

    def auth(self, uname, password):
        self._session.post('https://juick.com/login',
                           params={'username': uname, 'password': password})
        logger.info('Got cookies: %r', self._session.cookies)
        self._session.auth = uname, password

    users = _method('users')
    messages = _method('messages')
    thread = _method('thread')

    def webfeed(self, uname, **kwargs):
        MAX_RETRIES = 5
        TIMEOUT = 1
        url = 'https://juick.com/{0}/'.format(uname)

        for retry in xrange(MAX_RETRIES):
            logger.info('Juick.webfeed%r', kwargs)
            r = self._session.get(url, params=kwargs)
            logger.debug('Juick.webfeed%r -> %s %s',
                         kwargs, r.status_code, r.reason)

            if r.status_code // 100 != 5:
                break

            logger.info('[%d / %d] Got %s %s, retrying in %ss...',
                        retry + 1, MAX_RETRIES,
                        r.status_code, r.reason, TIMEOUT)
            time.sleep(TIMEOUT)

        r.raise_for_status()
        p = lxml.etree.HTML(r.content)
        return [
            int(x[4:])
            for x in p.xpath('//section[@id="content"]/ul/li/@id')
            if x.startswith('msg-')
        ]


def find_user(juick, uname):
    user_info = juick.users(uname=uname)
    assert len(user_info) == 1
    return user_info[0]['uid']


def fetch_all_messages_from_webfeed(juick, uname, before_mid=None):
    while True:
        mids = juick.webfeed(uname, before=before_mid)
        if not mids:
            break

        for mid in mids:
            yield juick.thread(mid=mid)
            before_mid = mid


def fetch_all_messages(juick, uname, before_mid=None):
    user_id = find_user(juick, uname)
    while True:
        try:
            messages = juick.messages(
                user_id=user_id, before_mid=before_mid)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                break  # no more messages available
            else:
                raise

        for message in messages:
            mid = message['mid']
            yield juick.thread(mid=mid)
            before_mid = mid


def main():
    logging.basicConfig()

    parser = argparse.ArgumentParser()
    parser.add_argument('username',
                        help='Target user name')
    parser.add_argument('-v', '--verbose',
                        help='Increase output verbosity',
                        action='count')
    parser.add_argument('--auth',
                        help='Log in as target user',
                        action='store_true')

    args = parser.parse_args()
    if args.verbose > 1:
        logger.setLevel(logging.DEBUG)
    elif args.verbose > 0:
        logger.setLevel(logging.INFO)

    dirname = uname = args.username
    if args.auth:
        dirname += '.private'

    juick = Juick()
    if args.auth:
        password = getpass.getpass('Juick password for {0}: '.format(uname))
        juick.auth(uname, password)

    if not os.path.isdir(dirname):
        os.mkdir(dirname)

    def prev_mids():
        pattern = os.path.join(dirname, '*.json')
        for filename in glob.iglob(pattern):
            base, _ = os.path.splitext(os.path.basename(filename))
            if base.isdigit():
                yield int(base)

    try:
        last_mid = min(prev_mids())
        logger.info('Resuming from %s...', last_mid)
    except ValueError:
        last_mid = None

    for thread in fetch_all_messages_from_webfeed(juick, uname, last_mid):
        filename = '{0}.json'.format(thread[0]['mid'])
        path = os.path.join(dirname, filename)
        with codecs.open(path, 'w', 'utf-8') as f:
            json.dump(
                thread, f,
                ensure_ascii=False,
                indent=2,
            )


if __name__ == '__main__':
    main()