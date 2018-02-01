from flask import Flask, request, redirect, url_for
from rauth.service import OAuth1Service

twitter = OAuth1Service(
    name='twitter',
    consumer_key='TWITTER KEY',
    consumer_secret='TWITTER SECRET',
    request_token_url = 'https://api.twitter.com/oauth/request_token',
    access_token_url = 'https://api.twitter.com/oauth/access_token',
    authorize_url = 'https://api.twitter.com/oauth/authorize',
)
request_token, request_token_secret = twitter.get_request_token(method='GET')

app = Flask(__name__)
app.debug = True

@app.route('/')
def index():
    token = request.args.get('oauth_token',None)
    verifier = request.args.get('oauth_verifier', None)

    if (token and verifier):
        print 'TOKEN: ', token
        print 'VERIFIER: ', verifier
        
        resp =  twitter.get_access_token(
            'POST',
            request_token = request_token,
            request_token_secret = request_token_secret,
            data = {'oauth_verifier': verifier}
        )
        
        data = resp.content
       
        access_token = data['oauth_token']
        access_token_secret = data['oauth_token_secret']

        return 'ACCESS_TOKEN: ' + access_token + ' | ACCESS_TOKEN_SECRET: ' + access_token_secret
    else:
        return redirect(url_for('login'))

@app.route('/login')
def login():
    authorize_url = twitter.get_authorize_url(request_token)
    print authorize_url
    return redirect(authorize_url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8999)
