import json

from flask import Flask, url_for, redirect, session
from flask_login import (UserMixin, login_required, login_user, logout_user, current_user)
from flask_googlelogin import GoogleLogin


users = {}

app = Flask(__name__)
app.config.update(
    SECRET_KEY='',
    GOOGLE_LOGIN_CLIENT_ID='',
    GOOGLE_LOGIN_CLIENT_SECRET='',
    GOOGLE_LOGIN_REDIRECT_URI='http://peaceful-thicket-9865.herokuapp.com/oauth2callback',
    GOOGLE_LOGIN_SCOPES='https://www.googleapis.com/auth/userinfo.email')

googlelogin = GoogleLogin(app)

class User(UserMixin):
    def __init__(self, userinfo):
        self.id = userinfo['id']
        self.name = userinfo['name']
        self.picture = userinfo.get('picture')
        self.email = userinfo.get('email')

@googlelogin.user_loader
def get_user(userid):
    return users.get(userid)

@app.route('/oauth2callback')
@googlelogin.oauth2callback
def login(token, userinfo, **params):
    user = users[userinfo['id']] = User(userinfo)
    login_user(user)
    session['token'] = json.dumps(token)
    session['extra'] = params.get('extra')
    return redirect(params.get('next', url_for('home')))

@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    return """
        <p>Logged out</p>
        <p><a href="/">Return to /</a></p>
        """

@app.route('/')
def index():
    return 'Hello world'

@app.route('/home')
@login_required
def home():
    return """
        <p>Hello, %s</p>
        <p><img src="%s" width="100" height="100"></p>
        <p>Token: %r</p>
        <p>Extra: %r</p>
        <p><a href="/logout">Logout</a></p>
        """ % (current_user.email, current_user.picture, session.get('token'),
               session.get('extra'))


@app.route('/api/addexpense')
@login_required
def api_addexpense():
    req = request.get_json()
    print(req)

"""
All code related to data model
"""