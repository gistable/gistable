#encoding: utf-8
import csv
import time
from datetime import datetime, timedelta
import tweepy


def login():
    auth = tweepy.BasicAuthHandler('user', 'pass')
    return tweepy.API(auth)


def get_user_timeline(screen_name, page, api):
    user = api.get_user(screen_name)
    timeline = user.timeline(page=page)
    return timeline


def save_tweets():
    page = i = 1
    file = csv.writer(open('tweets.csv', 'w'))
    while True:
        try:
            timeline = get_user_timeline('screen name', page, login())
        except:
            delta = datetime.now() + timedelta(hours=1)
            print 'Dormindo até: %s' % delta.strftime('%H:%M:%S')
            time.sleep(60 * 60)
            timeline = get_user_timeline('screen name', page, login())

        if len(timeline) == 0:
            break
        for tweet in timeline:
            file.writerow([tweet.id, tweet.text.encode('utf-8'),
                            tweet.created_at.strftime('%d/%m/%y')])
            i += 1
        print 'pag: %d tweet:%d' % (page, i)
        page += 1

if __name__ == '__main__':
    save_tweets()
