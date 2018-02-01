#!/usr/bin/env python
import itertools
import json
import logging
import sys
import time
import traceback

# oauth2 is available at https://github.com/simplegeo/python-oauth2
import oauth2

# Basic preferences / configuration

MY_BLOG = '**********'
POST_TYPES = ('photo',)
MIN_NOTE_COUNT = 5000
INTERVAL = 360
FOLLOW_INTERVAL = 5
FOLLOW_COUNT = 2
REBLOG_INTERVAL = 1
REBLOG_COUNT = 1
VERBOSITY = 'DEBUG'

CONSUMER_KEY = '**************************************************'
CONSUMER_SECRET = '**************************************************'
# OAuth tokens can be obtained using codingjester's oauth_tumblr.py
# which is available at https://gist.github.com/2296339
TOKEN_KEY = '**************************************************'
TOKEN_SECRET = '**************************************************'

# Constants

OAUTH_BASE_URL = 'http://www.tumblr.com/oauth/'
REQUEST_TOKEN_URL = OAUTH_BASE_URL + 'request_token'
AUTHORIZATION_URL = OAUTH_BASE_URL + 'authorize'
ACCESS_TOKEN_URL = OAUTH_BASE_URL + 'access_token'

API_BASE_URL = 'http://api.tumblr.com/v2/'
FOLLOWING_URL = API_BASE_URL + 'user/following?offset=%s'
FOLLOWBACK_TAG_URL = API_BASE_URL + 'tagged?tag=follow-back&api_key=' + CONSUMER_KEY
FOLLOW_URL = API_BASE_URL + 'user/follow'
DASHBOARD_URL = API_BASE_URL + 'user/dashboard'
REBLOG_URL = API_BASE_URL + 'blog/%s.tumblr.com/post/reblog' % MY_BLOG

client = oauth2.Client(
    oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET),
    oauth2.Token(TOKEN_KEY, TOKEN_SECRET))
# This was necessary at some point but I don't remember when or why
client.disable_ssl_certificate_validation = True

log = logging.getLogger('autotumble')
log.addHandler(logging.StreamHandler(sys.stdout))
log.setLevel(getattr(logging, VERBOSITY))

def req(*args):
    """Send an OAuth request through the client."""
    log.debug('Sending request %r' % (args,))
    resp, content = client.request(*args)
    #if not resp['status'].startswith('2'):
    #    log.warn('Got HTTP status %s' % resp['status'])
    j = json.loads(content)
    log.debug('%s %s' % ((j['meta']['status'], j['meta']['msg'])))
    if not str(j['meta']['status']).startswith('2'):
        raise ValueError(j['meta']['status'])
    return j

def random_follow(n=1):
    """Follow n new users from the #follow-back tag."""
    followback = req(FOLLOWBACK_TAG_URL, 'GET')
    for post in reversed(followback['response']):
        if n <= 0:
            return
        if post['blog_name'] in following:
            # Already following this blog
            continue
        follow = req(FOLLOW_URL, 'POST',
            'url=%s.tumblr.com' % post['blog_name'])
        following.add(post['blog_name'])
        n -= 1

def random_reblog(n=1):
    """Reblog n random posts from the dashboard."""
    dashboard = req(DASHBOARD_URL, 'GET')
    for post in dashboard['response']['posts']:
        if n <= 0:
            return
        if post['note_count'] < MIN_NOTE_COUNT or \
                post['type'] not in POST_TYPES:
            continue
        reblog = req(REBLOG_URL, 'POST',
            'id=%s&reblog_key=%s' % (post['id'], post['reblog_key']))
        n -= 1

if __name__ == '__main__':
    
    # Get currently followed blogs
    
    log.info('Getting list of blogs already followed')
    following = set()
    offset = 0
    while True:
        rfollowing = req(FOLLOWING_URL % offset, 'GET')
        for blog in rfollowing['response']['blogs']:
            following.add(blog['name'])
        if len(rfollowing['response']['blogs']) < 20:
            break
        offset += 20
        time.sleep(10)
    log.info('Currently following %s blogs' % len(following))
    time.sleep(30)
    
    # Enter main loop
    
    for i in itertools.count():
        log.info('Iteration %s' % i)
        
        try:
            if not i % FOLLOW_INTERVAL:
                random_follow(FOLLOW_COUNT)
            if not i % REBLOG_INTERVAL:
                random_reblog(REBLOG_COUNT)
        except Exception:
            traceback.print_exc()
        for j in xrange(INTERVAL):
            sys.stderr.write('\rWaiting %s more second' % (INTERVAL - j))
            sys.stderr.write('s ' if (INTERVAL - j != 1) else ' ')
            sys.stderr.flush()
            time.sleep(1)
        sys.stderr.write('\n')