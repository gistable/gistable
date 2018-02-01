# internal
import time

# external
import flask
from twython import Twython

# local
from env import ENV


#INITS

# flask application
app = flask.Flask(__name__)
app.config['URL'] = ENV['URL']
app.config['SECRET_KEY'] = ENV['SECRET_KEY']

# twython object
twitter = Twython(
    ENV['API_KEY'],
    ENV['API_SECRET'],
)


# FUNCTIONS

def force_unfollow_fans(twitter):
    '''
    fans == people that follow you that you dont follow back

    we block and them unblock them to force an unfollow
    '''
    user_name = twitter.verify_credentials()['screen_name']
    followers = twitter.get_followers_ids()['ids']
    following = twitter.get_friends_ids()['ids']
    fans = set(followers) - set(following)

    for fan in fans:
        fan_name = twitter.lookup_user(user_id=fan)[0]['screen_name']
        twitter.create_block(user_id=fan)
        twitter.destroy_block(user_id=fan)
        print('@{} force unfollowed @{}'.format(user_name, fan_name))
        time.sleep(10) # to avoid going too far past the rate limit


# ROUTES

@app.route('/')
def index():
    return 'go to /login'

@app.route('/login')
def login():
    auth = twitter.get_authentication_tokens(callback_url=ENV['URL']+'/callback')
    flask.session['oauth_token']        = auth['oauth_token']
    flask.session['oauth_token_secret'] = auth['oauth_token_secret']
    return flask.redirect(auth['auth_url'])

@app.route('/callback')
def callback():
    twitter = Twython(
        ENV['API_KEY'],
        ENV['API_SECRET'],
        flask.session['oauth_token'],
        flask.session['oauth_token_secret'],
    )
    auth_creds = twitter.get_authorized_tokens(flask.request.args['oauth_verifier'])
    twitter = Twython(
        ENV['API_KEY'],
        ENV['API_SECRET'],
        auth_creds['oauth_token'],
        auth_creds['oauth_token_secret'],
    )
    force_unfollow_fans(twitter)
    return 'done!'


if __name__ == '__main__':
    app.run(debug=True, port=int(ENV['PORT']))
