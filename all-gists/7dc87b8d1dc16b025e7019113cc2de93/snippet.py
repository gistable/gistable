# -*- coding: utf-8 -*-
from urllib.parse import urlunsplit

import requests
from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session


def register_app(client_name, host, redirect_uris='urn:ietf:wg:oauth:2.0:oob',
                 scopes='read write follow'):
    """Register application

    Usage:

        >>> d = register_app('myapp', host='pawoo.net')
        >>> d
        {'id': 1234, 'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob', 'client_id': '...', 'client_secret': '...'}

    """
    data = {
        'client_name': client_name,
        'redirect_uris': redirect_uris,
        'scopes': scopes,
    }
    resp = requests.post("https://{host}/api/v1/apps".format(host=host), data=data)
    resp.raise_for_status()
    return resp.json()


def fetch_token(client_id, client_secret, email, password, host, scope=('read', 'write', 'follow')):
    token_url = "https://{host}/oauth/token".format(host=host)
    client = LegacyApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(token_url=token_url, username=email, password=password,
                              client_id=client_id, client_secret=client_secret, scope=scope)
    return token


class Mstdn:
    """Mastodon API

    Usage:

        >>> token = fetch_token(...)
        >>> mstdn = Mstdn(token)
        >>> mstdn.toot("テスト")

    """
    def __init__(self, token, scheme='https', host='pawoo.net'):
        self.scheme = scheme
        self.host = host
        self.session = requests.Session()
        self.session.headers.update({'Authorization': 'Bearer ' + token['access_token']})

    def _build_url(self, path):
        return urlunsplit([self.scheme, self.host, path, '', ''])

    def _request(self, method, url, data=None, params=None):
        kwargs = {
            'data': data or {},
            'params': params or {}
        }
        resp = self.session.request(method, url, **kwargs)
        resp.raise_for_status()
        return resp

    def home_timeline(self):
        url = self._build_url('/api/v1/timelines/home')
        return self._request('get', url)

    def toot(self, status):
        url = self._build_url('/api/v1/statuses')
        return self._request('post', url, data={'status': status})