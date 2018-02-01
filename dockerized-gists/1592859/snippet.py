# Twitter's Trends API has been in flux since Feburary 2011 when Mining the Social Web was published
# and unfortunately, this is causing some confusion in the earliest examples.
# See also https://dev.twitter.com/docs/api/1/get/trends

# Note that the twitter package that's being imported is from https://github.com/sixohsix/twitter
# If you have first done an "easy_install pip" to get pip, you could easily install the latest
# version directly from GitHub as follows:
# $ pip install -e git+http://github.com/sixohsix/twitter.git#egg=github-pip-install


import twitter
twitter_api=twitter.Twitter(domain="api.twitter.com", api_version='1')
WORLD_WOE_ID = 1 # The Yahoo! Where On Earth ID for the entire world
world_trends = twitter_api.trends._(WORLD_WOE_ID) # get back a callable
[ trend for trend in world_trends()[0]['trends'] ] # call the callable and iterate through the trends returned

# sample results
#
# [{u'url': u'http://twitter.com/search/%23TheGame', u'query': u'%23TheGame', u'events': None, u'promoted_content': None, u'name': u'#TheGame'}, {u'url': u'http://twitter.com/search/%22Woman%20Thou%20Art%20Loosed%22', u'query': u'%22Woman%20Thou%20Art%20Loosed%22', u'events': None, u'promoted_content': None, u'name': u'Woman Thou Art Loosed'}, {u'url': u'http://twitter.com/search/%23FelicidadesNOTEAMA', u'query': u'%23FelicidadesNOTEAMA', u'events': None, u'promoted_content': None, u'name': u'#FelicidadesNOTEAMA'}, {u'url': u'http://twitter.com/search/%22Lmao%20Jason%22', u'query': u'%22Lmao%20Jason%22', u'events': None, u'promoted_content': None, u'name': u'Lmao Jason'}, {u'url': u'http://twitter.com/search/%22Pooch%20Hall%22', u'query': u'%22Pooch%20Hall%22', u'name': u'Pooch Hall', u'promoted_content': None, u'events': None}, {u'url': u'http://twitter.com/search/McHottie', u'query': u'McHottie', u'events': None, u'promoted_content': None, u'name': u'McHottie'}, {u'url': u'http://twitter.com/search/Brandy', u'query': u'Brandy', u'events': None, u'promoted_content': None, u'name': u'Brandy'}, {u'url': u'http://twitter.com/search/Moesha', u'query': u'Moesha', u'events': None, u'promoted_content': None, u'name': u'Moesha'}, {u'url': u'http://twitter.com/search/Derwin', u'query': u'Derwin', u'events': None, u'promoted_content': None, u'name': u'Derwin'}, {u'url': u'http://twitter.com/search/%23PumpedUpKicks', u'query': u'%23PumpedUpKicks', u'events': None, u'promoted_content': None, u'name': u'#PumpedUpKicks'}]