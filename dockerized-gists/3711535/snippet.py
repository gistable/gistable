#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: dawn
'''

import  urllib, urllib2, cookielib, json
from datetime import datetime

EMAIL = 'xxx@gmail.com'
PASSWD = 'YOUR-PASSWORD'
EXPIRES_DAY = 250 #超XX天无更新，取消订阅

cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
headers = {'Authorization': ''}
TOKEN = None

def login(email, passwd):
    '''
        登录
    '''
    post_data = {'service': "reader", 'Email': email, 'Passwd': passwd}
    ur = 'https://www.google.com/accounts/ClientLogin'
    responseData = opener.open(ur, urllib.urlencode(post_data)).read()
    if not responseData:
        return False

    def getArgs(data, name):
        name = name if name[-1] == '=' else name + '='
        b = data.find(name)
        e = data.find('\n', b)
        return data[b + len(name):e]

    sid = getArgs(responseData, 'SID=') #responseData[0].split('=')[1]
    auth = getArgs(responseData, 'Auth=') #responseData[2].split('=')[1]

    headers['Authorization'] = 'GoogleLogin auth=%s' % auth
    sidCookie = cookielib.Cookie(version=0, name='SID', value=sid, port=None, port_specified=False,
        domain='.google.com', domain_specified=False, domain_initial_dot=False, path='/', path_specified=True,
        secure=False, expires=1600000000, discard=True, comment=None, comment_url=None, rest={'HttpOnly': None},
        rfc2109=False)
    cj.set_cookie(sidCookie)
    return True


def openAuthorizedUrl(url, data=None, method='GET'):
    request = urllib2.Request(url, headers=headers)
    request.get_method = lambda: method
    responseData = opener.open(request, urllib.urlencode(data) if data else None).read()
    return responseData


def getSubscriptions():
    url = 'https://www.google.com/reader/api/0/subscription/list?output=json'
    return json.loads(openAuthorizedUrl(url))


def checkSubscription(process, id, expiresDay=365):
    '''
        过期检查
    '''
    url = 'https://www.google.com/reader/api/0/stream/contents/%s?n=1&output=json' % urllib.quote(id)
    feed = json.loads(openAuthorizedUrl(url))
    updated = datetime.fromtimestamp(int(feed['updated']))
    expiresDays = (datetime.now() - updated).days
    title = feed['title'].encode('utf-8')
    if expiresDays >= expiresDay:
        result = unsubscribe(id)
        print '%d.\tUNSUBSCRIBE:%s\t LastUpdate:%s \t ExpiresDay:%d \t\t - %s' % (
            process, result, updated, expiresDays, title)
    else:
        print '%d.\tPASS\t LastUpdate:%s \t ExpiresDay:%d \t\t - %s' % (process, updated, expiresDays, title)


def unsubscribe(id):
    url = 'https://www.google.com/reader/api/0/subscription/edit?client=py-dawn'
    post_data = {'s': id, 'ac': 'unsubscribe', 'T': TOKEN}
    return openAuthorizedUrl(url, post_data, method='POST')


def getToken():
    url = 'https://www.google.com/reader/api/0/token?client=py-dawn'
    return openAuthorizedUrl(url)

if __name__ == '__main__':
    if login(EMAIL, PASSWD):
        TOKEN = getToken()
        print 'GET TOKEN:%s' % TOKEN
        subs = getSubscriptions()["subscriptions"]
        print 'GET subs:%s' % len(subs)
        for (index, sub) in enumerate(subs):
            checkSubscription(index + 1, sub['id'], expiresDay=EXPIRES_DAY)
        else:
            print'COMPLETED!'