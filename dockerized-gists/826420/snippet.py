#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
フレームワークとして Flask(http://flask.pocoo.org/) を、OAuth ライブラリとして oauth2(http://pypi.python.org/pypi/oauth2/) を利用したサンプルプログラムです。

下のコードを保存して (oauth_consumer.py とします)、YOUR_CONSUMER_KEY, YOUR_CONSUMER_SECRET となっている部分を自分の consumer_key, consumer_secret で置き換えます。

$ python oauth_consumer.py

... で起動してから http://localhost:5000 に Web ブラウザでアクセスして下さい。
"""
import urlparse

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        from django.utils import simplejson as json

import flask
from flask import (
    session, request, redirect, url_for, render_template_string, 
)
import oauth2 as oauth

CONSUMER_KEY='YOUR_CONSUMER_KEY'
CONSUMER_SECRET='YOUR_COUSEMER_SECRET'
SECRET_KEY = 'YOUR_SECRET_KEY'
SCOPE = 'read_public'
DEBUG = True

REQUEST_TOKEN_URL='https://www.hatena.com/oauth/initiate'
ACCESS_TOKEN_URL='https://www.hatena.com/oauth/token'
AUTHORIZE_URL='https://www.hatena.ne.jp/oauth/authorize'

app = flask.Flask(__name__)
app.secret_key = SECRET_KEY
app.config['DEBUG'] = DEBUG
consumer = oauth.Consumer(CONSUMER_KEY, CONSUMER_SECRET)

TEMPLATE = """
<html>
    <head>
    <titile></title>
    </head>
    <body>
        {% if user %}
            <p>
                Hello {{ user.display_name }}(id:{{ user.url_name }})
                <img src="{{ user.profile_image_url }}">
            </p>
            <p><a href="{{ url_for('logout') }}">LOGOUT</a></p>
        {% else %}
            <p>Hello GUEST<img src="http://cdn.www.st-hatena.com/users/ri/ritou/profile.gif"></p>
            <p><a href="{{ url_for('login') }}">LOGIN</a></p>
        {% endif %}
    </body>
</html>
"""

@app.route('/')
def index():
    ctx = { 'user': None}
    access_token = session.get('access_token')
    if access_token:
        # access_tokenなどを使ってAPIにアクセスする
        token = oauth.Token(access_token['oauth_token'], access_token['oauth_token_secret'])
        client = oauth.Client(consumer, token)
        resp, content = client.request('http://n.hatena.com/applications/my.json')
        ctx['user'] = json.loads(content)
    return render_template_string(TEMPLATE, **ctx)

# リクエストトークン取得から認証用URLにリダイレクトするための関数
@app.route('/login')
def login():
    # リクエストトークンの取得
    client = oauth.Client(consumer)
    resp, content = client.request('%s?scope=%s&oauth_callback=%s%s' % \
            (REQUEST_TOKEN_URL, SCOPE, request.host_url, 'on-auth'))
    # セッションへリクエストトークンを保存しておく
    session['request_token'] = dict(urlparse.parse_qsl(content))
    # 認証用URLにリダイレクトする
    return redirect('%s?oauth_token=%s' % (AUTHORIZE_URL, session['request_token']['oauth_token']))

# セッションに保存されたトークンを破棄しログアウトする関数
@app.route('/logout')
def logout():
    if session.get('access_token'):
        session.pop('access_token')
    if session.get('request_token'):
        session.pop('request_token')
    return redirect(url_for('index'))

# 認証からコールバックされ、アクセストークンを取得するための関数
@app.route('/on-auth')
def on_auth():
    # リクエストトークンとverifierを用いてアクセストークンを取得
    request_token = session['request_token']
    token = oauth.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
    token.set_verifier(request.args['oauth_verifier'])
    client = oauth.Client(consumer, token)
    resp, content = client.request(ACCESS_TOKEN_URL)
    # アクセストークンをセッションに記録しておく
    session['access_token'] = dict(urlparse.parse_qsl(content)) 
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
