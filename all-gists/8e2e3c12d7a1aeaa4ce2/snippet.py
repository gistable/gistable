# -*- coding: utf-8 -*-

from datetime import *
import tweepy

now = datetime.today() - timedelta(0,60)
text =  str(now.year) + u"年" + str(now.month) + u"月" + str(now.day) + u"日" + str(now.hour) + u"時" + str(now.minute) + u"分のTwitterトレンドです。"

#print text

CONSUMER_KEY = "" # ご自身で取得してください
CONSUMER_SECRET = "" # ご自身で取得してください
ACCESS_TOKEN = "" # ご自身で取得してください
ACCESS_TOKEN_SECRET = "" # ご自身で取得してください

auth = tweepy.OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN,ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)

api.update_with_media(filename='./now.png',status=text)