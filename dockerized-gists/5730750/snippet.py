#!/usr/bin/env python

import sys
import urllib
import requests
from BeautifulSoup import BeautifulSoup

def get_google_auth_session(username, password):
    session = requests.Session()
    google_accounts_url = 'http://accounts.google.com'
    authentication_url = 'https://accounts.google.com/ServiceLoginAuth'
    stack_overflow_url = 'http://stackoverflow.com/users/authenticate'

    r = session.get(google_accounts_url)
    dsh = BeautifulSoup(r.text).findAll(attrs={'name' : 'dsh'})[0].get('value').encode()
    auto = r.headers['X-Auto-Login']
    follow_up = urllib.unquote(urllib.unquote(auto)).split('continue=')[-1]
    galx = r.cookies['GALX']

    payload = {'continue' : follow_up,
               'followup' : follow_up,
               'dsh' : dsh,
               'GALX' : galx,
               'pstMsg' : 1,
               'dnConn' : 'https://accounts.youtube.com',
               'checkConnection' : '',
               'checkedDomains' : '',
               'timeStmp' : '',
               'secTok' : '',
               'Email' : username,
               'Passwd' : password,
               'signIn' : 'Sign in',
               'PersistentCookie' : 'yes',
               'rmShown' : 1}

    r = session.post(authentication_url, data=payload)

    if r.url != authentication_url: # XXX
        print "Logged in"
    else:
        print "login failed"
        sys.exit(1)

    payload = {'oauth_version' : '',
               'oauth_server' : '',
               'openid_username' : '',
               'openid_identifier' : ''}
    r = session.post(stack_overflow_url, data=payload)
    return session

def get_so_auth_session(email, password):
    session = requests.Session()
    r = session.get('http://stackoverflow.com/users/login')
    fkey = BeautifulSoup(r.text).findAll(attrs={'name' : 'fkey'})[0]['value']

    payload = {'openid_identifier': 'https://openid.stackexchange.com',
               'openid_username': '',
               'oauth_version': '',
               'oauth_server': '',
               'fkey': fkey,
               }
    r = session.post('http://stackoverflow.com/users/authenticate', allow_redirects=True, data=payload)
    fkey = BeautifulSoup(r.text).findAll(attrs={'name' : 'fkey'})[0]['value']
    session_name = BeautifulSoup(r.text).findAll(attrs={'name' : 'session'})[0]['value']

    payload = {'email': email,
               'password': password,
               'fkey': fkey,
               'session': session_name}

    r = session.post('https://openid.stackexchange.com/account/login/submit', data=payload)
    
    error = BeautifulSoup(r.text).findAll(attrs={'class' : 'error'})
    if len(error) != 0:
        print "ERROR:", error[0].text
        sys.exit(1)
    return session

if __name__ == "__main__":
    prov = raw_input('Choose your openid provider [1 for StackOverflow, 2 for Google]: ')
    name = raw_input('Enter your OpenID address: ')
    pswd = getpass('Enter your password: ')
    if '1' in prov:
        so = get_so_auth_session(name, pswd)
    elif '2' in prov:
        so = get_google_auth_session(name, pswd)
    else:
        print "Error no openid provider given"

    r = so.get('http://stackoverflow.com/inbox/genuwine')
    print r.json()