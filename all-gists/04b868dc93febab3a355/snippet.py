#-*-coding:utf-8-*-

import hashlib
import hmac
import time
import requests

HMAC_KEY = '5tT!TQkf5fYbabw5?KL2659XgL^JgxWw8r9Y+bAvGwP-QfteQL'

class TanTan(object):

    base_url = 'https://core.tantanapp.com'

    def __init__(self, auth_token, geo_lat, geo_lon):
        self.auth_token = auth_token
        self.geo_lat = geo_lat
        self.geo_lon = geo_lon

    def request(self, method, endpoint, **kwargs):
        url = self.base_url + endpoint
        headers = kwargs.pop('headers', {})
        headers.update(self.get_default_headers())
        r = requests.request(method, url, headers=headers, **kwargs)
        data = r.json()
        if data['meta'].get('code') != 200:
            raise RuntimeError(data)
        else:
            return data

    def get_default_headers(self):
        return {
            'Geolocation': 'geo:{self.geo_lat},{self.geo_lon};u=65'.format(self=self),
            'User-Agent': 'Putong/2.1.1.1 iOS/9.2.1 iPhone/iPhone8,1 (iPhone 6s)',
            'Authorization': self.get_auth_string(),
        }

    def get_auth_string(self, timestamp=None):
        if not timestamp:
            timestamp = int(time.time())

        message = '{timestamp}.{auth_token}'.format(
            timestamp=timestamp, auth_token=self.auth_token
        )
        hmac_string = self.hmac_sha1(HMAC_KEY, message)

        return 'MAC ["1","android1.7.1","{timestamp}","{auth_token}","{hmac}"]'.format(
            timestamp=timestamp, auth_token=self.auth_token, hmac=hmac_string
        )

    @staticmethod
    def hmac_sha1(key, message):
        return hmac.new(key, message, hashlib.sha1).digest().encode('base64').strip()

    def like(self, user_id):
        endpoint = '/v1/users/me/relationships/{user_id}'.format(user_id=user_id)
        return self.request('put', endpoint, json={'state': 'liked'})

    def get_user_list(self):
        data = self.request('get', '/v1/users', params={
            'search': 'suggested',
            'with': 'questions,contacts'
        })
        users = data['data']['users']
        return users


def main():
    tantan = TanTan('xxxxxxxxxxxxxxxx', 39.9724, 116.4861)
    while True:
        users = tantan.get_user_list()
        for user in users:
            print u'Like {id} - {name}'.format(**user)
            tantan.like(user['id'])
            time.sleep(0.5)


if __name__ == '__main__':
    main()