# twitter oauth example using urllib
#
# Many uses of the twitter api don't require authenticating as other users,
# but the documentation centers around it.  In this example, we're using the
# twitter-provided access key & secret (keys['token']) rather than going
# through the handshake.

import json
import urllib2

# leah culver's oauth library
from oauth import oauth

# key,value tuples
keys = dict(
    consumer = ('...', '...'),
    token = ('...', '...'),
)

consumer = oauth.OAuthConsumer(*keys['consumer'])
access_token = oauth.OAuthToken(*keys['token'])
sig_method = oauth.OAuthSignatureMethod_HMAC_SHA1()

def fetch(url, parameters=None):
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(
        consumer, token=access_token, http_url=url, parameters=parameters
    )
    oauth_request.sign_request(sig_method, consumer, access_token)
    headers = oauth_request.to_header()
    headers['User-Agent'] = 'Example Twitter OAuth Agent'
    request = urllib2.Request(url, headers=headers)
    return json.loads(urllib2.urlopen(request).read())

if __name__ == '__main__':
    from pprint import pprint
    sample = 'http://api.twitter.com/1/account/rate_limit_status.json'
    print "Getting %s" % sample
    pprint(fetch(sample))
