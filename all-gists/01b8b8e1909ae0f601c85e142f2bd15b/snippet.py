#!/usr/bin/env python
# encoding=utf-8

import codecs
import json
import os
import sys

from pushbullet import Pushbullet
from weibo import Client
from xtls.util import BeautifulSoup

APP_HOME = os.path.join(os.path.expanduser("~"), '.weibo_monitor')
if not os.path.isdir(APP_HOME):
    os.mkdir(APP_HOME)

PUSHBULLET = Pushbullet('PUSH_BULLET_API_KEY')

APP_KEY = '*****'
APP_SECRET = '******'
CALLBACK_URL = 'https://api.weibo.com/oauth2/default.html'
AUTH_URL = 'https://api.weibo.com/oauth2/authorize'
USERID = '******'
PASSWD = '*******'


class ObjectDict(dict):
    def __getattr__(self, key):
        if key in self:
            return self[key]
        return None

    def __setattr__(self, key, value):
        self[key] = value


class User(ObjectDict):
    def __init__(self, id_, avatar_hd, description, followers_count, friends_count, location, name, url):
        super(User, self).__init__(
            id=id_,
            avatar_hd=avatar_hd,
            description=description,
            followers_count=followers_count,
            friends_count=friends_count,
            location=location,
            name=name,
            url=url
        )

    def diff(self, other):
        diff = []
        if self.name != other.name:
            diff.append(u'昵称')
        if self.avatar_hd != other.avatar_hd:
            diff.append(u'头像')
        if self.description != other.description:
            diff.append(u'简介')
        if self.location != other.location:
            diff.append(u'地址')
        if self.url != other.url:
            diff.append(u'博客')
        return diff

    def __eq__(self, other):
        return self.id == other.id


class Tweet(ObjectDict):
    def __init__(self, id_, text, source, geo, retweeted_status=None):
        super(Tweet, self).__init__(
            id=id_,
            text=text,
            source=source,
            geo=geo,
            retweeted_status=retweeted_status
        )


class Weibo(ObjectDict):
    """
    {
        "user": #User,
        "tweets": [#Tweet, #Tweet, ...],
        "last": Tweet.id
    }
    """

    def __init__(self, user, tweets=None, last=0):
        if tweets is None:
            tweets = []
        super(Weibo, self).__init__(
            user=user,
            tweets=tweets,
            last=last
        )


def get_weibo(uid):
    path = os.path.join(APP_HOME, '{}.wm'.format(uid))
    if not os.path.exists(path):
        return Weibo(None)
    with codecs.open(path, 'rb', encoding='utf-8') as fp:
        data = json.loads(fp.read())
    return Weibo(get_user(data),
                 tweets=[get_tweet(t) for t in data['tweets']],
                 last=data['last'])


def save_weibo(uid, data):
    data = json.dumps(data, ensure_ascii=False, sort_keys=True)
    path = os.path.join(APP_HOME, '{}.wm'.format(uid))
    with codecs.open(path, 'wb', encoding='utf-8') as fp:
        fp.write(data)


def get_user(status):
    return User(
        status['user']['id'],
        status['user']['avatar_hd'],
        status['user']['description'],
        status['user']['followers_count'],
        status['user']['friends_count'],
        status['user']['location'],
        status['user']['name'],
        status['user']['url'],
    )


def get_tweet(status):
    return Tweet(
        id_=status['id'],
        text=status['text'],
        source=status['source'],
        geo=status['geo'],
        retweeted_status=None
    )


def send_noti(title, body):
    print u'send <{}>, <{}>'.format(title, body)
    PUSHBULLET.push_note(title, body)


def main(uid):
    client = Client(APP_KEY, APP_SECRET, CALLBACK_URL, username=USERID, password=PASSWD)
    data = client.get('statuses/friends_timeline')
    statuses = [status for status in data['statuses'] if status['user']['id'] == uid]
    statuses.sort(key=lambda x: x['id'], reverse=True)
    if not statuses:
        return
    weibo = get_weibo(uid)
    newest = get_user(statuses[0])

    if weibo.user is None:
        weibo.user = newest

    diff = weibo.user.diff(newest)

    if diff:
        weibo.user = newest
        send_noti(u'{} 的微博资料更新'.format(weibo.user.name),
                  u'{} 的微博资料有如下更新：\n{}'.format(weibo.user.name, u'\n'.join(diff)))

    tweet = get_tweet(statuses[0])
    has_new = weibo.last != tweet.id

    if has_new:
        weibo.last = tweet.id
        weibo.tweets.append(tweet)
        send_noti(u'{} 发新微博啦~'.format(weibo.user.name),
                  u'{} 通过【{}】发送了一条微博，内容是：\n{}'.format(
                      weibo.user.name,
                      BeautifulSoup(tweet.source).getText(),
                      tweet.text
                  ))

    if has_new or diff:
        save_weibo(uid, weibo)


if __name__ == '__main__':
    main(int(sys.argv[1]))
