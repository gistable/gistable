"""
Taken from my suggestion at:
https://groups.google.com/forum/#!msg/tweepy/OSGRxOmkzL4/yaNT9fL9FAIJ

Note that this is an incomplete snippet; you'll need to create the API auth object.
"""

import simplejson as json
import tweepy

class MyModelParser(tweepy.parsers.ModelParser):
    def parse(self, method, payload):
        result = super(MyModelParser, self).parse(method, payload)
        result._payload = json.loads(payload)
        return result

api = tweepy.API(auth, parser=MyModelParser())
results = api.user_timeline(screen_name='twitter')

for s in results._payload:
    print  json.dumps(s)

