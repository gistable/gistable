from twython import Twython


## Defining access_token as a function so that the token may be cached
## using a decorator as follows,
##
## get_access_token = cache_textfile('.twython-token')(access_token)
## 
def access_token(auth_client):
    return auth_client.obtain_access_token()


def app_auth_client(app_key, app_secret):    
    tw_auth = Twython(app_key, app_secret, oauth_version=2)
    return Twython(app_key, access_token=access_token(tw_auth))


if __name__ == '__main__':
    # example
    twitter = app_auth_client(APP_KEY, APP_SECRET)
    results = twitter.search(q='pyconindia2013', count='100')