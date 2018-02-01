#!/usr/bin/env python

# NOTE: This sample app does NOT use SSL. Before deploying this code to a
# server environment, you should ENABLE SSL to avoid exposing your API
# access token in plaintext.

# To run this demo app:
# 1. Save this file to your computer as `server.py`
#
# 2. In the Inbox Developer Portal, create a new application. Replace the
#    CLIENT_ID and CLIENT_SECRET variables below with the App ID and App
#    Secret of your application.
#
# 3. In the Inbox Developer Portal, edit your application and add the
#    callback URL: http://localhost:6002/login_callback
#
# 4. On the command line, `cd` to the folder where you saved the file
#
# 5. On the command line, run `python ./server.py`
#    - You may need to install Python: https://www.python.org/download/
#    - You may need to install dependencies using pip:
#      (http://pip.readthedocs.org/en/latest/installing.html)
#      pip install flask requests urllib
#
# 6. In the browser, visit http://localhost:6002/
#

from base64 import b64encode
from flask import Flask, url_for, session, request, redirect, Response
import requests
import uuid

try:
    from urllib import urlencode #Python 2.7
except ImportError:
    from urllib.parse import urlencode #Python 3.0+

from json import loads as load_json

# Replace these!
CLIENT_ID = 'YOUR INBOX APP ID'
CLIENT_SECRET = 'YOUR INBOX APP SECRET'

INBOX_BASE_URL = 'https://beta.inboxapp.com/'

app = Flask(__name__)
app.debug = True
app.secret_key = 'secret'

OAUTH_AUTHORIZE_URL = INBOX_BASE_URL+"oauth/authorize"
OAUTH_ACCESS_TOKEN_URL = INBOX_BASE_URL+"oauth/token"

assert(CLIENT_ID != 'YOUR INBOX APP ID')
assert(CLIENT_ID != 'YOUR INBOX APP SECRET')


@app.route('/')
def index():
    # If we have an access_token, we may interact with the Inbox Server
    if 'access_token' in session:
        token = session['access_token']
        try:
            token_encoded = b64encode(token + ':')
        except TypeError:
            token_encoded = b64encode(bytes(token + ':', 'UTF-8')).decode('UTF-8')

        auth_hdrs = {'Authorization': 'Basic ' + token_encoded}

        # Get the default namespace
        resp = requests.get(INBOX_BASE_URL + '/n/',
                            headers=auth_hdrs, verify=False)
        resp = load_json(resp.text)
        user_ns = resp[0]['namespace']

        # Get the messages
        resp = requests.get(INBOX_BASE_URL +
                            '/n/{}/messages/?limit=1'.format(user_ns),
                            headers=auth_hdrs, verify=False)
        resp = load_json(resp.text)[0]

        # Format the output
        text = "<html><h1>Here's a message from your Inbox:</h1><b>From:</b> "
        for sender in resp['from']:
            text += "{} &lt;{}&gt;".format(sender['name'], sender['email'])
        text += "<br /><b>Subject:</b> " + resp['subject']
        text += "<br /><b>Body:</b> " + resp['body']
        text += "</html>"

        # Return result to the client
        return Response(text)

    return """
    <html>
    <form action="/login" method="get">
        Email:<input type="text" name="login_hint">
        <input type="submit" value="Login">
    </form>
    </html>"""


@app.route('/login')
def login():
    args = {
        'redirect_uri': url_for('.login_callback', _external=True),
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'scope': 'email',  # default
        'state': uuid.uuid1(),
        'login_hint': request.args.get('login_hint')
    }

    url = OAUTH_AUTHORIZE_URL + '?' + urlencode(args)
    return redirect(url)


@app.route('/login_callback')
def login_callback():
    if 'error' in request.args:
        error = request.args.get('error', None)
        if error == 'access_denied':
            return "Access was denied. Reason: %s" % \
                request.args.get('reason', 'Unknown')
        else:
            return "Unknown error: {0}".format(error)

    authorization_code = request.args.get('code')
    assert authorization_code

    args = {
        'client_id': CLIENT_ID,
        'code': authorization_code,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'redirect_uri': url_for('.login_callback', _external=True),
    }

    headers = {'Content-type': 'application/x-www-form-urlencoded',
               'Accept': 'text/plain'}
    data = urlencode(args)

    resp = requests.post(OAUTH_ACCESS_TOKEN_URL,
                         data=data, headers=headers, verify=False).json()

    session['access_token'] = resp[u'access_token']
    return index()


if __name__ == '__main__':
    import os
    os.environ['DEBUG'] = 'true'
    app.run(host='0.0.0.0', port=6002)