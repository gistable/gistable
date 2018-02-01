# Twitter

from app.config import TWITTER_APP_KEY, TWITTER_APP_SECRET

twitter_oauth = oauth.remote_app(
    'twitter',
    consumer_key=TWITTER_APP_KEY,
    consumer_secret=TWITTER_APP_SECRET,
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
)


# Facebook

from app.config import FACEBOOK_APP_KEY, FACEBOOK_APP_SECRET

facebook_oauth = oauth.remote_app(
    'facebook',
    consumer_key=FACEBOOK_APP_KEY,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'email'},
    base_url='https://graph.facebook.com',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth'
)


# Instagram

from app.config import INSTAGRAM_APP_KEY, INSTAGRAM_APP_SECRET

instagram_oauth = oauth.remote_app(
    'instagram',
    consumer_key=INSTAGRAM_APP_KEY,
    consumer_secret=INSTAGRAM_APP_SECRET,
    base_url='https://api.instagram.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://api.instagram.com/oauth/access_token',
    authorize_url='https://api.instagram.com/oauth/authorize',
)


# VK

from app.config import VK_APP_KEY, VK_APP_SECRET

vk_oauth = oauth.remote_app(
    'vk',
    consumer_key=VK_APP_KEY,
    consumer_secret=VK_APP_SECRET,
    request_token_params={'scope': 'email'},
    base_url='https://api.vk.com/method/',
    request_token_url=None,
    access_token_url='https://oauth.vk.com/access_token',
    authorize_url='https://oauth.vk.com/authorize'
)