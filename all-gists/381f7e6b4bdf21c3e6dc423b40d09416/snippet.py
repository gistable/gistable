#!/bin/python
import tweepy
#following Oauth credentials can be obtained by creating twitter app
cfg = {
    "consumer_key"        : "<consumer_key>",
    "consumer_secret"     : "<consumer_secret>",
    "access_token"        : "<access_token>",
    "access_token_secret" : "<access_token_secret>"
    }


def get_api(cfg):
    auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
    auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
    return tweepy.API(auth)


def main():
    api = get_api(cfg)
    while True:
        for status in api.user_timeline('pyconindia'):
            current_status_id = status.id
            print current_status_id
            break
        retweet_status = api.get_status(current_status_id).retweeted
        print retweet_status
        if retweet_status:
            print("already retwitted")
        else:
            print("retweeting")
            api.retweet(current_status_id)

if __name__ == "__main__":
    main()