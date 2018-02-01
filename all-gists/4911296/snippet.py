#!/usr/bin/env python

import cookielib
import os
from contextlib import closing
import re
import getpass
import webbrowser
import sys

import requests


class AlgoSpot(object):
    login_url = 'https://algospot.com/accounts/login/?next=/'

    def __init__(self):
        cookiefile_path = os.path.join(os.path.expanduser('~'), '.kaka')
        self.cj = cj = cookielib.LWPCookieJar(cookiefile_path)
        try:
            cj.load()
        except IOError:
            pass
        self.opener = requests.Session()
        self.opener.cookies = cj

    def login(self, username, password):
        html = self._request(self.login_url)
        csrf_token = self._get_csrf_token(html)
        data = {
            'username': username,
            'password': password,
            'csrfmiddlewaretoken': csrf_token,
        }
        html = self._request(self.login_url, data)
        ok = self._is_loggedin(html)
        if ok:
            self.cj.save()
        return ok

    def is_loggedin(self):
        html = self._request('https://algospot.com')
        return self._is_loggedin(html)

    def ensure_login(self):
        if self.is_loggedin():
            return
        while True:
            username = raw_input('Username: ')
            password = getpass.getpass()
            if self.login(username, password):
                break
            print 'Login failure.'

    def submit(self, problem, lang, content):
        url = 'https://algospot.com/judge/problem/submit/{}'.format(problem)
        html = self._request(url)
        csrf_token = self._get_csrf_token(html)
        data = {
            'csrfmiddlewaretoken': csrf_token,
            'language': lang,
            'source': content,
        }
        self._request(url, data)

    def open_recent_submission(self, problem):
        webbrowser.open('https://algospot.com/judge/submission/recent/?user={}&problem={}'.format(self.username, problem))

    def _is_loggedin(self, html):
        if 'href="/accounts/logout/"' in html:
            self.username = re.search('<a href="/user/profile/\d+" class="username">([^<]+)</a>', html).group(1).strip()
            return True
        else:
            return False
    def _get_csrf_token(self, html):
        return re.search("name='csrfmiddlewaretoken' value='(\w+)'", html).group(1)
    def _request(self, url, data=None):
        if data is None:
            r = self.opener.get(url)
        else:
            r = self.opener.post(url, data, headers={'Referer': self.login_url})
        return r.content


ext_to_lang = {
    '.java' : 'java',
    '.scala': 'scala',
    '.hs'   : 'hs',
    '.py'   : 'py',
    '.js'   : 'js',
    '.rb'   : 'rb',
    '.c'    : 'cpp',
    '.cpp'  : 'cpp',
    '.cxx'  : 'cpp',
    '.cc'   : 'cpp',
}
def guess_language(filename):
    base, ext = os.path.splitext(filename)
    ext = ext.lower()
    return ext_to_lang.get(ext)
def guess_problem(filename):
    filename = os.path.basename(filename)
    base, ext = os.path.splitext(filename)
    return re.search('[0-9A-Z]+', base.upper()).group(0)

assert guess_language('/path/to/boggle.py') == 'py'
assert guess_problem('/path/to/boggle.py') == 'BOGGLE'
assert guess_problem('/path/to/snail-recursion.py') == 'SNAIL'
assert guess_problem('/path/to/tripathcnt_dp.py') == 'TRIPATHCNT'

def main(filepath):
    lang = guess_language(filepath)
    if not lang:
        print 'Language guess fail.'
        return

    problem = guess_problem(filepath)

    try:
        with open(filepath) as f:
            content = f.read()
    except IOError:
        print "Can't open/read file."
        return

    site = AlgoSpot()
    site.ensure_login()
    site.submit(problem, lang, content)
    site.open_recent_submission(problem)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: {} <file>'.format(sys.argv[0])
        sys.exit(1)
    main(sys.argv[1])
