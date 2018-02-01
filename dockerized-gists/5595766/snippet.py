#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 此脚本不再更新, 毕竟要依赖第三方pycurl库.
# 重写的脚本不再依赖非标准库, 感兴趣的见: https://github.com/isayme/v2ex

import sys
import string
try:
    import pycurl2 as pycurl
except:
    import pycurl
import urllib
import StringIO

V2EX_DEBUG = False

V2EX_AUTH_VALUE = ''
V2EX_COOKIE = 'auth=' + V2EX_AUTH_VALUE

V2EX_URL_START = 'https://v2ex.com'
V2EX_MISSION = V2EX_URL_START + '/mission/daily'
V2EX_COIN_URL = '/mission/daily/redeem?once='

def body_write(buf):
    sys.stdout.write(buf)

def write_null(buf):
    pass

# normal init  
def curl_init(curl):
    curl.setopt(curl.NOSIGNAL, 1)
    curl.setopt(curl.NOPROGRESS, 1)
    curl.setopt(curl.SSL_VERIFYPEER, 0)
    curl.setopt(curl.SSL_VERIFYHOST, 0)
    curl.setopt(curl.TIMEOUT, 10)
    curl.setopt(curl.AUTOREFERER, 1)
    curl.setopt(curl.COOKIEFILE, '')
    curl.setopt(curl.COOKIELIST, 'ALL')

    curl.setopt(curl.FOLLOWLOCATION, 0)

    curl.fp = StringIO.StringIO()
    curl.setopt(curl.WRITEFUNCTION, write_null)
    #curl.setopt(curl.WRITEFUNCTION, curl.fp.write)
   
    curl.setopt(curl.HTTPHEADER, ["Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", \
            "User-Agent: Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0",
            "Accept-Language: en-US,en;q=0.5",    
            "Referer: " + V2EX_MISSION])
    
    if True == V2EX_DEBUG:
        curl.setopt(curl.VERBOSE, 1)
    else:
        curl.setopt(curl.VERBOSE, 0)

# set cookie    
def set_cookie(curl, cookie):
    curl.setopt(curl.COOKIE, cookie)

def check_status(curl, code):
    ret = curl.getinfo(curl.RESPONSE_CODE)
    if code != ret:
        print "url [%s] return code is : %d" % (curl.getinfo(curl.EFFECTIVE_URL), ret)
        return -1
    return 0

def parse_arg(data, s, t):
    start = data.find(s)
    if -1 == start:
        return None

    start = start + len(s)

    data = data[start:]
    end = data.find(t)
    if -1 == end:
        return None

    return data[0: end]

def get_once(data):
    return parse_arg(data, V2EX_COIN_URL, '\'')

if __name__ == '__main__':
    # global init
    pycurl.global_init(pycurl.GLOBAL_ALL) 
    curl = pycurl.Curl()

    # curl object init
    curl_init(curl)

    # auth mode
    set_cookie(curl, V2EX_COOKIE)
    
    # broser index for some cookie
    curl.setopt(curl.WRITEFUNCTION, write_null)
    curl.setopt(curl.URL, V2EX_URL_START)
    curl.perform()

    # broser mission url to get `once` code
    curl.setopt(curl.WRITEFUNCTION, curl.fp.write)
    curl.setopt(curl.URL, V2EX_MISSION)
    curl.perform()

    # HTTP code must be 200
    if -1 == check_status(curl, 200):
        print 'maybe your auth cookie not valid'
        sys.exit(-1)

    data = curl.fp.getvalue()
    if True == V2EX_DEBUG:
        print data

    once = get_once(data)
    if None == once:
        print '"once" not found, maybe you already got coins'
        sys.exit(-1)

    v2ex_coin_url = V2EX_URL_START + V2EX_COIN_URL + once
    print v2ex_coin_url

    # get coin
    curl.setopt(curl.WRITEFUNCTION, write_null)
    curl.setopt(curl.URL, v2ex_coin_url)
    curl.perform()

    # HTTP code must be 302
    if -1 == check_status(curl, 302):
        print 'maybe something wrong'
        sys.exit(-1)
    
    # clean curl
    curl.close()
    pycurl.global_cleanup() 
