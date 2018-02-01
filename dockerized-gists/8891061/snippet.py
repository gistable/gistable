"""
As Hubic web services are deprecated, this is a small script to request
access and refresh token. It starts a flask server at http://localhost:5000/, the
users fill the hubic authentication form with its navigator and obtain the
credentials returned by the application.

You need requests-oauthlib and flask:
  pip install flask
  pip install requests-oauthlib

The client and id secret are valid but users can create their own application
on hubic and change the values of these entries.
"""

from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for
from flask.json import jsonify
import os
import uuid; 

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)

client_id = 'api_hubic_dMCUY8MLynmkpIgdrj2D8GlbaSPemHAE'
client_secret = '9TgfdUFvjTCXgOahwz0ai1kEh03RrvDKI0kw4kZ3hCCbC2pQPtvJSdcKlTyFz3Q6'

authorization_base_url = 'https://api.hubic.com/oauth/auth/?'
token_url = 'https://api.hubic.com/oauth/token/'
redirect_uri = "http://localhost:5000/callback"

scope = u"usage.r,account.r,getAllLinks.r,credentials.r,activate.w,links.drw"

state = 'RandomString_' + str(uuid.uuid4().get_hex().upper()[0:10])

@app.route("/")
def start():
    hubic = OAuth2Session(client_id, scope=scope, state=state, redirect_uri=redirect_uri)
    authorization_url, state_back = hubic.authorization_url(authorization_base_url)
    return redirect(authorization_url)

@app.route("/callback", methods=["GET"])
def callback():
    hubic = OAuth2Session(client_id, state=state,redirect_uri=redirect_uri)
    token = hubic.fetch_token(token_url, client_secret=client_secret,
                              authorization_response=request.url)
    session['oauth_token'] = token
    return redirect(url_for('.account'))


@app.route("/account", methods=["GET"])
def account():
    hubic = OAuth2Session(client_id, token=session['oauth_token'])
    return jsonify(session['oauth_token'])


if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.run(debug=True)
