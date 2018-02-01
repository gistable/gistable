import httplib

import base64
import contextlib
import simplejson
import urllib

from django.conf import settings

def stripe_fetch(resource, method='GET', params=None, secret=settings.STRIPE_SECRET, prefix='/v1'):
    headers = {
        'Accept': 'application/json',
        'User-Agent': 'Clutch 1.0',
        'Authorization': 'Basic %s' % (base64.b64encode('%s:' % (secret,)),),
    }
    if params:
        flattened = {}
        for key, val in params.iteritems():
            if getattr(val, 'iteritems', None) is not None:
                for sub_key, sub_val in val.iteritems():
                    flattened['%s[%s]' % (key, sub_key)] = sub_val
            else:
                flattened[key] = val
        body = urllib.urlencode(flattened)
    else:
        body = ''
    with contextlib.closing(httplib.HTTPSConnection('api.stripe.com')) as conn:
        conn.request(method, prefix + resource, body, headers)
        raw_data = conn.getresponse().read()
    return simplejson.loads(raw_data)