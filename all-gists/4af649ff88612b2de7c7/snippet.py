#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from oauthlib.oauth2 import (
    FatalClientError, OAuth2Error, TokenExpiredError, MobileApplicationClient
)
from requests_oauthlib import OAuth2Session, TokenUpdated


client_id = 'xxxx'
client_secret = 'yyyy'
redirect_uri = 'https://api.shanbay.com/oauth2/auth/success/'
authorization_base_url = 'https://api.shanbay.com/oauth2/authorize/'
token_url = 'https://api.shanbay.com/oauth2/token/'
token_file = 'token.json'


def userinfo(api):
    r = api.get('https://api.shanbay.com/account/')
    print r.json()


def get_token():
    client = MobileApplicationClient(client_id)
    api = OAuth2Session(client=client, redirect_uri=redirect_uri)

    authorization_url, state = api.authorization_url(authorization_base_url)
    print 'Please go here and authorize,', authorization_url

    redirect_response = raw_input('Paste the full redirect URL here:')

    token = api.token_from_fragment(redirect_response)

    with open(token_file, 'w') as f:
        f.write(json.dumps(token, indent=2))
    return api

try:
    with open(token_file) as f:
        token = json.loads(f.read())
    api = OAuth2Session(client_id, token=token)
    userinfo(api)
except (
    TokenExpiredError, TokenUpdated, OAuth2Error, FatalClientError, ValueError
) as e:
    api = get_token()
    userinfo(api)