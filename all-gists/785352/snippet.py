### Note: This depends on my fork of a fork of python-oauth2
###       https://github.com/offlinelabs/python-oauth2
### (The original python-oauth2 doesn't support OAuth 2.0. It's just the second
### OAuth 1.0 library. dgouldin created a fork which has the Client2 class, and
### I tweaked it to support the latest draft of the OAuth 2.0 spec, as implemented
### by the Foursquare v2 API.)

>>> from django.conf import settings
>>> import oauth2, json

>>> c = oauth2.Client2(settings.FOURSQUARE_CONSUMER_KEY, settings.FOURSQUARE_CONSUMER_SECRET_KEY, settings.FOURSQUARE_OAUTH_BASE)

### Not user-authorized
>>> (headers, content) = c.request("https://api.foursquare.com/v2/venues/83633")
>>> if headers['status'] != '200':
...     raise Exception(content)
>>> response = json.loads(content)["response"]
>>> print "%(id)s - %(name)s" % response["venue"]
>>> print "ALL HAIL %(id)s - %(firstName)s %(lastName)s !!" % response["venue"]["mayor"]["user"]

### User authorization
>>> print c.authorization_url(redirect_uri=settings.FOURSQUARE_REGISTERED_CALLBACK_URL, endpoint='authenticate')
# Go visit that URL, click allow, look at the code in the URL param

>>> code = 'CODE_YOU_GOT_IN_THE_URL_PARAM'
>>> at = c.access_token(code, redirect_uri=settings.FOURSQUARE_REGISTERED_CALLBACK_URL, grant_type='authorization_code')["access_token"]
>>> print at

>>> (headers, content) = c.request('https://api.foursquare.com/v2/users/self', access_token=at)
>>> if headers['status'] != '200':
...     raise Exception(content)
>>> response = json.loads(content)["response"]
>>> print "%(id)s - %(firstName)s %(lastName)s" % response["user"]
