#!/usr/bin/python2
# -*- coding: utf-8 -*-

#
# This's an auto-sign script for vnet.link
# You should install PIL first, for Ubuntu 14.04:
# sudo apt-get build-dep python-imaging python-pip -y && pip install Pillow
#
# 12/3/2016 Cody Chan <int64ago@gmail.com>
# To support me, register from https://vnet.link/?rc=36900
#

from PIL import Image, ImageEnhance
import urllib, urllib2, cookielib, io, json, time

NUM_TABLE = [[[1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 0, 0, 0, 0, 1, 1, 1], [1, 1, 0, 0, 0, 0, 0, 0, 1, 1], [1, 0, 0, 1, 1, 1, 1, 0, 0, 1], [0, 0, 1, 1, 1, 1, 1, 1, 0, 0], [0, 0, 1, 1, 1, 1, 1, 1, 0, 0], [1, 0, 0, 1, 1, 1, 1, 0, 0, 1], [1, 1, 0, 0, 0, 0, 0, 0, 1, 1], [1, 1, 1, 0, 0, 0, 0, 1, 1, 1]], [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 0, 1, 1, 1, 1, 1, 1, 0], [1, 0, 0, 1, 1, 1, 1, 1, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1, 1, 1, 1, 0], [1, 1, 1, 1, 1, 1, 1, 1, 1, 0], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]], [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 0, 1, 1, 1, 1, 1, 1, 0], [1, 0, 0, 1, 1, 1, 1, 1, 0, 0], [0, 0, 1, 1, 1, 1, 1, 0, 0, 0], [0, 1, 1, 1, 1, 1, 0, 0, 1, 0], [0, 1, 1, 1, 1, 0, 0, 1, 1, 0], [0, 0, 1, 1, 0, 0, 1, 1, 1, 0], [1, 0, 0, 0, 0, 1, 1, 1, 1, 0], [1, 1, 0, 0, 1, 1, 1, 1, 1, 0]], [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 0, 1, 1, 1, 1, 1, 1, 0, 1], [0, 0, 1, 1, 1, 1, 1, 1, 0, 0], [0, 1, 1, 1, 1, 1, 1, 1, 1, 0], [0, 1, 1, 1, 0, 1, 1, 1, 1, 0], [0, 1, 1, 1, 0, 1, 1, 1, 1, 0], [0, 0, 1, 0, 0, 0, 1, 1, 0, 0], [1, 0, 0, 0, 1, 0, 0, 0, 0, 1], [1, 1, 0, 1, 1, 1, 0, 0, 1, 1]], [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 0, 0, 1, 1, 1], [1, 1, 1, 1, 0, 0, 0, 1, 1, 1], [1, 1, 1, 0, 0, 1, 0, 1, 1, 1], [1, 1, 0, 0, 1, 1, 0, 1, 1, 1], [1, 0, 0, 1, 1, 1, 0, 1, 1, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1, 0, 1, 1, 1]], [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 1, 1, 0, 1, 1], [0, 0, 0, 0, 0, 1, 1, 0, 0, 1], [0, 1, 1, 1, 0, 1, 1, 1, 0, 0], [0, 1, 1, 0, 1, 1, 1, 1, 1, 0], [0, 1, 1, 0, 1, 1, 1, 1, 1, 0], [0, 1, 1, 0, 0, 1, 1, 1, 0, 0], [0, 1, 1, 1, 0, 0, 0, 0, 0, 1], [1, 1, 1, 1, 1, 0, 0, 0, 1, 1]], [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 0, 0, 0, 0, 0, 0, 1, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 1], [0, 0, 1, 1, 1, 0, 1, 1, 0, 0], [0, 1, 1, 1, 0, 1, 1, 1, 1, 0], [0, 1, 1, 1, 0, 1, 1, 1, 1, 0], [0, 0, 1, 1, 0, 0, 1, 1, 0, 0], [1, 0, 0, 1, 1, 0, 0, 0, 0, 1], [1, 1, 1, 1, 1, 1, 0, 0, 1, 1]], [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [0, 1, 1, 1, 1, 1, 1, 1, 0, 0], [0, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 1, 1, 1, 1, 1, 0, 0, 1, 1], [0, 1, 1, 1, 1, 0, 0, 1, 1, 1], [0, 1, 1, 1, 0, 0, 1, 1, 1, 1], [0, 1, 1, 0, 0, 1, 1, 1, 1, 1], [0, 0, 0, 0, 1, 1, 1, 1, 1, 1], [0, 0, 0, 1, 1, 1, 1, 1, 1, 1]], [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 0, 1, 1, 1, 0, 0, 1, 1], [1, 0, 0, 0, 1, 0, 0, 0, 0, 1], [0, 0, 1, 0, 0, 0, 1, 1, 0, 0], [0, 1, 1, 1, 0, 1, 1, 1, 1, 0], [0, 1, 1, 1, 0, 1, 1, 1, 1, 0], [0, 0, 1, 0, 0, 0, 1, 1, 0, 0], [1, 0, 0, 0, 1, 0, 0, 0, 0, 1], [1, 1, 0, 1, 1, 1, 0, 0, 1, 1]], [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 0, 0, 1, 1, 1, 1, 1, 1], [1, 0, 0, 0, 0, 1, 1, 0, 0, 1], [0, 0, 1, 1, 0, 0, 1, 1, 0, 0], [0, 1, 1, 1, 1, 0, 1, 1, 1, 0], [0, 1, 1, 1, 1, 0, 1, 1, 1, 0], [0, 0, 1, 1, 0, 1, 1, 1, 0, 0], [1, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 1, 0, 0, 0, 0, 0, 0, 1, 1]]]

def gen_table(threshold):
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)
    return table
        
def image_to_number(img):
    number = 0
    max_count = 0
    for i in range(10):
        count = 0
        for x in range(9):
            for y in range(10):
                if img.getpixel((x, y)) == NUM_TABLE[i][x][y]:
                    count += 1
        if count > max_count:
            max_count = count
            number = i
    return number
        

def image_to_string(img):
    enhancer = img.convert('L')
    enhancer = ImageEnhance.Brightness(enhancer)
    enhancer = enhancer.enhance(4)
    enhancer = enhancer.point(gen_table(150),'1')
    enhancer = enhancer.crop((9, 3, 63, 13))
    string = ''
    for i in range(6):
        img = enhancer.crop((9*i, 0, 9*(i+1), 10))
        string += str(image_to_number(img))
    return string

def login_and_sign(username, password):
    cookie = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))

    data = {'username': username, 'password': password}
    opener.open('https://vnet.link/login_do', urllib.urlencode(data))
    
    res = opener.open('https://vnet.link/openapi/v1/regcode?action=checkcode')
    image = Image.open(io.BytesIO(res.read()))
    code = image_to_string(image)
    res = opener.open('https://vnet.link/openapi/v1/regcode?action=gift1&num=' + code)
    tt = time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
    print('[%s] %s' % (tt, json.loads(res.read())['data'].encode('UTF-8')))

login_and_sign('username', 'password')

