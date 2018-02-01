#!/usr/bin/env python2

# Author: Chris Dellin <cdellin@gmail.com>
# Date: 2016-09-14
# Script to scrape a working OAuth code from Google
# using the approach from dequis and hastebrot
# for use with hangups, purple-hangouts, etc.

# Requires packages python-gi and gir1.2-webkit-3.0 on Ubuntu 16.04.

# If you are using this with the Pidgin UI, run the script with no
# arguments, and paste the resulting OAuth code into the box labeled
# "Please paste the Google OAuth code here".

# If you are using this with libpurple, pass the --redeem argument,
# and the script will also redeem your auth code for a refresh token,
# which can be set directly as the account password (e.g. in the
# <password> field of your .purple/accounts.xml file).

import argparse
import json
import urllib
import pygtk
pygtk.require('2.0')
from gi.repository import Gtk as gtk
from gi.repository import WebKit as webkit
from gi.repository import GObject as gobject
from gi.repository import Soup as soup

parser = argparse.ArgumentParser()
parser.add_argument('--redeem', default=False, action='store_true')
args = parser.parse_args()

# create window with a webview
window = gtk.Window()
window.set_resizable(True)
window.set_default_size(350,580)
window.connect("delete_event", lambda w,e: False)
window.connect("destroy", lambda w: gtk.main_quit())
scrolled = gtk.ScrolledWindow(None, None)
webview = webkit.WebView()
scrolled.add(webview)
window.add(scrolled)
window.show_all()

# hook up a cookie jar
# http://stackoverflow.com/a/39296977/5228520
cookiejar = soup.CookieJarText.new('', False)
cookiejar.set_accept_policy(soup.CookieJarAcceptPolicy.ALWAYS)
session = webkit.get_default_session()
session.add_feature(cookiejar)

# open google page to request auth code
# see https://github.com/tdryer/hangups/issues/260#issuecomment-246578670
# and https://github.com/tdryer/hangups/issues/260#issuecomment-247512300
# thanks dequis and hastebrot!
get_params = {
   'hl': 'en',
   'scope': 'https://www.google.com/accounts/OAuthLogin',
   'client_id': '936475272427.apps.googleusercontent.com',
}
uri_entrypoint = 'https://accounts.google.com/o/oauth2/programmatic_auth?' + urllib.urlencode(get_params)
webview.open(uri_entrypoint)

# register callback to auto-close on success or failure
allowed_uris = [
   uri_entrypoint,
   'https://accounts.google.com/ServiceLogin?',
   'https://accounts.google.com/signin/challenge/']
def mycallback():
   uri = webview.get_uri()
   if uri is None or any([uri.startswith(pre) for pre in allowed_uris]):
      return True
   gtk.main_quit()
gobject.timeout_add(100, mycallback)

# start application (stops on window close or callback)
gobject.threads_init()
gtk.main()

# read from cookie jar
oauth_codes = []
for c in cookiejar.all_cookies():
   if c.get_domain() == 'accounts.google.com' and c.get_name() == 'oauth_code':
      oauth_codes.append(c.get_value())
for oauth_code in oauth_codes:
   print('Found OAuth code: {}'.format(oauth_code))
if not oauth_codes:
   print('No oauth_codes found!')
 
if len(oauth_codes) == 1 and args.redeem:
   print('Redeeming OAuth code for refresh token ...')
   # These parameters borrowed from the prpl-hangouts source code
   # (see https://bitbucket.org/EionRobb/purple-hangouts/src/default/hangouts_auth.c)
   request_uri = 'https://www.googleapis.com/oauth2/v3/token'
   request_data = {
      'client_id': '936475272427.apps.googleusercontent.com',
      'client_secret': 'KWsJlkaMn1jGLxQpWxMnOox-',
      'code': oauth_codes[0],
      'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
      'grant_type': 'authorization_code'
   }
   resp = json.loads(urllib.urlopen(request_uri, urllib.urlencode(request_data)).read())
   if 'refresh_token' in resp:
      print('Found refresh token: {}'.format(resp['refresh_token']))
      print('(Use this as your pidgin/finch/libpurple hangouts account password.)')
   elif 'error' in resp:
      print('Error: {} ({})'.format(resp['error_description'], resp['error']))
   else:
      print('Unknown error, response: {}'.format(resp))
      