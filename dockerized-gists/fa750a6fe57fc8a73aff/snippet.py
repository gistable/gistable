#!/usr/bin/env python2

# Dependencies:
# * Requests

# Simply change stuff and run the script

import time
import re
from hashlib import md5
import requests
from HTMLParser import HTMLParser

# Enter your username and password
UNAME = '106111101'
PASSWORD = '' # Fill it in suckers

BEAT_INTERVAL = 15
MIN_RELOGIN = 10

DOMAIN = 'https://192.168.20.1'
LOGIN_PORTAL = DOMAIN + '/auth1.html'
AUTH_PAGE = DOMAIN + '/auth.cgi'
HEARTBEAT = DOMAIN + '/usrHeartbeat.cgi'
LOGIN_STATUS = DOMAIN + '/loginStatusTop.html'
DYN_LOGIN_STATUS = DOMAIN + '/dynLoginStatus.html?1stLoad=yes'
LOGOUT = DOMAIN + '/dynLoggedOut.html?didLogout=yes'

class InputFieldParser(HTMLParser):
    def handle_starttag(self, tag, attr_pairs):
        if tag != 'input':
            return
        attr_dict = dict(attr_pairs)
        if not 'name' in attr_dict:
            return
        if not 'value' in attr_dict:
            return
        name = attr_dict['name']
        value = attr_dict['value']
        if name == 'sessId':
            print 'Session ID,', value
            self.sess_id = value
        elif name == 'param2':
            print 'Random param,', value
            self.param2 = value
        elif name == 'id':
            print 'ID,',  value
            self.rid = value

def bake_cookies(p):
    cookies = {}
    cookies['SessId'] = p.sess_id
    page_seed = md5(p.param2 + PASSWORD).hexdigest()
    print 'PageSeed, ' + page_seed
    cookies['PageSeed'] = page_seed
    # Dunno?
    cookies['temp'] = 'temp'
    return cookies

def make_form(p):
    form = {}
    form['param1'] = ''
    form['param2'] = p.param2
    form['id'] = p.rid
    form['sessId'] = p.sess_id
    form['select2'] = 'English'
    form['uName'] = UNAME
    form['pass'] = PASSWORD
    form['digest'] = ''
    return form

def req_login_page():
    # Disable SSL cert verification
    resp = requests.get(LOGIN_PORTAL, verify = False)
    parser = InputFieldParser()
    parser.feed(resp.text)
    return parser

def parse_beat(data):
    val = re.findall('var remTime=(\d*);', data)[0]
    return int(val)

def do_login():
    p = req_login_page()
    print 'Got login page'
    cookies = bake_cookies(p)
    form = make_form(p)
    login_req = requests.post(AUTH_PAGE, data = form, cookies = cookies, verify = False)
    if login_req.status_code != 200:
        raise Exception('Error in logging in')
    if login_req.text.find('auth.html') != -1:
        raise Exception('Invalid credentials/Already logged in')
    print 'Logged in successfully'
    requests.get(LOGIN_STATUS, cookies = cookies, verify = False)
    requests.get(DYN_LOGIN_STATUS, cookies = cookies, verify = False)
    return cookies

def main():
    cookies = do_login()
    try:
        while True:
            beat_req = requests.post(HEARTBEAT, cookies = cookies, verify = False)
            rem_time = parse_beat(beat_req.text)
            print 'Heatbeat ..*..', rem_time
            if rem_time < MIN_RELOGIN:
                print 'Re-logging in...'
                cookies = do_login()
            time.sleep(BEAT_INTERVAL)
    finally:
        print 'Exit. Logging out...'
        requests.get(LOGOUT, verify = False)


if __name__ == '__main__':
    main()
