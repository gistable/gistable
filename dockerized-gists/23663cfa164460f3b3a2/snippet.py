from hashlib import sha1
import random
import requests
import string
import time

# these come from your CloudShare account page
USER_ID = ''
KEY = ''

VERSION = '2'


def cloudshare(resource, **kw):
    url = 'https://use.cloudshare.com/API/v{}/{}'.format(VERSION, resource)
    token = ''.join(random.choice(string.digits) for x in range(10))
    params = {
        'UserApiId': USER_ID,
        'timestamp': int(time.time()),
        'token': token,
    }
    params.update(kw)
    signature = ''.join('{}{}'.format(k.lower(), v)
                        for k, v in sorted(params.items(), key=lambda x: x[0].lower()))
    signature = '{}{}{}'.format(KEY, resource.split('/')[-1].lower(), signature)
    params['HMAC'] = sha1(signature).hexdigest()
    res = requests.get(url, params=params)
    return res.json()

import pdb; pdb.set_trace()
# Example:
# cloudshare('ApiTest/Ping')
