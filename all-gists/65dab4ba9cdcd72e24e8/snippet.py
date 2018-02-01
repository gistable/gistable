#!/usr/bin/env python
from __future__ import print_function

import os.path
import glob
import json
import argparse
import sqlite3


def find_sessions(home, sessions):
    for session in sessions:
        for fname in glob.glob(os.path.join(home, '*', session + '.json')):
            yield session, os.path.basename(os.path.dirname(fname)), fname


def get_default_cookie_file():
    for fname in glob.glob(os.path.expanduser('~/.mozilla/firefox/*/cookies.sqlite')):
        return fname

    return None


def get_connection(path):
    return sqlite3.connect(path)


def get_fox_cookies(conn, domain):
    cur = conn.cursor()
    cur.execute('SELECT name, value, path, expiry, isSecure from moz_cookies where baseDomain = ?', (domain,))
    return cur.fetchall()


def update_session(conn, session, domain, fname):
    cookies = get_fox_cookies(conn, domain)
    if not cookies:
        return

    data = json.loads(open(fname).read())
    for name, value, path, expires, secure in cookies:
        cookie = {
            'value': value,
            'path': path,
            'expires': expires,
            'secure': bool(secure)
        }
        data['cookies'][name] = cookie

    with open(fname, 'bw') as f:
        f.write(json.dumps(data, sort_keys=True, ensure_ascii=False, indent=4).encode('utf-8'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Imports firefox cookies into httpie sessions')
    parser.add_argument('sessions', metavar='SESSION', nargs='+', help='session name')
    parser.add_argument('-H', '--http-home', dest='http_home',
        default=os.path.expanduser('~/.httpie/sessions'))
    parser.add_argument('-C', '--cookies', dest='cookies',
        default=get_default_cookie_file(), help='Path to firefox cookies. %(default)s')

    args = parser.parse_args()

    conn = get_connection(args.cookies)
    for session, domain, fname in find_sessions(args.http_home, args.sessions):
        update_session(conn, session, domain, fname)
