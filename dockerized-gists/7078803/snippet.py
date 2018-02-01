#!/usr/bin/env python
#encoding=utf-8
# Hacker Need Food!

import json
import os
import sys
from optparse import OptionParser
import urllib, urllib2, cookielib

url = 'http://fan.wandoulabs.com'
cookie_file = './.fancookie'
ldap_config = './.fanconfig'
ldap_user = None
ldap_pass = None

opt_parser = OptionParser()
opt_parser.add_option('-c', '--config',
                      action='store',
                      dest='config_file',
                      default=ldap_config,
                      help='Set LDAP user info config file, first line is ladp user, second line is ldap password, default is ./.fanconfig')

opt_parser.add_option('-r', '--random',
                      action='store_true',
                      dest='is_random',
                      default=False,
                      help='I\'m Feeling Lucky!')

opt_parser.add_option('-l', '--list',
                      action='store_true',
                      default=False,
                      dest='list_dishes',
                      help='List all dishes')

opt_parser.add_option('-o', '--orders',
                      action='store_true',
                      default=False,
                      dest='list_orders',
                      help='List orders')

opt_parser.add_option('-n', '--new-order',
                      action='store',
                      default='',
                      dest='new_order',
                      help=u'make new orders, format: "[shop1]<dish name 1>:count1 [shop1]<dish name 2>:count2", e.g. (麦当劳)新奥尔良烤翅:1 or 新奥尔良烤翅:1')

def read_config(config_file):
    if os.path.exists(config_file) == False:
        return -1
    with open(config_file) as fp:
        global ldap_user, ldap_pass
        content = fp.read()
        ldap_user, ldap_pass = content.split('\n')[0],content.split('\n')[1]
        ldap_user = ldap_user.lstrip().rstrip()
        ldap_pass = ldap_pass.lstrip().rstrip()
    return 0

def login(username, passwd):
    if os.path.exists(cookie_file):
        os.remove(cookie_file)
    data = {'mail': username, 'passwd': passwd}
    req = urllib2.Request(url + '/api/auth?type=json')
    data = urllib.urlencode(data)

    cookie_jar = cookielib.MozillaCookieJar(cookie_file)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
    response = opener.open(req,data)
    ret = json.loads(response.read())
    if ret['ret'] == 1:
        cookie_jar.save()
        return True
    else:
        sys.stderr.write('Login failed, Set LDAP user info config file, first line is ladp user, second line is ldap password, default is ./.fanconfig')
        sys.stderr.write('\n')
        exit(-1)

def request(url, data = None):
    cookie_jar = cookielib.MozillaCookieJar(cookie_file)
    cookie_jar.load()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
    req = urllib2.Request(url)
    response = None
    if data != None:
        response = opener.open(req,urllib.urlencode(data))
    else:
        response = opener.open(req)
    return response.read()

# orders: [{'name':, 'count':, 'price':}, ... ]
def do_order(orders):
    print 'Load all dishes...'
    dishes = list_dishes(False)
    print 'Load orders'
    post_order = []
    for rec in orders:
        name = rec['name']
        price = int(rec['price'])
        if dishes.get(name) and len(dishes[name]) == 1:
            d = dishes[name][0]
            post_order.append({'name': d['name'], 'from': d['shop'], 'number': rec['count'], 'price': d['price']})
        else:
            print 'no such dish or dishes with same name:', name
            print 'try fuzzy find ...'
            for n in dishes:
                for d in dishes[n]:
                    if d['shop'].encode('utf-8') + n.encode('utf-8') == name and int(d['price']) == int(price) * 100:
                        print 'dish found:', name
                        post_order.append({'name': d['name'], 'from': d['shop'], 'number': rec['count'], 'price': d['price']})
    form = {'id':ldap_user + '@wandoujia.com', 'order':post_order}
    t = json.dumps(form)
    data = {}
    data['json'] = t
    try:
        print request(url + '/api/order', data)
    except urllib2.HTTPError, e:
        print e.read()
        if e.code == 403:
            print 'post failed, please make order before 4:00 pm'

def my_order():
    pass

def disorder():
    pass

def list_dishes(display = True):
    shops = json.loads(request(url + '/api/all'))
    ret = []
    for shop in shops:
        u = url + urllib2.quote('/api/' + shop['url'].encode('utf-8'))
        shop_dish_category = json.loads(request(u))
        for cat in shop_dish_category:
            for dish in cat['dishes']:
                if display:
                    print shop['name'].encode('utf-8'),dish['name'].encode('utf-8'), int(dish['price']) / 100
                ret.append({'shop': shop['name'], 'name': dish['name'], 'price': dish['price']})
    dish_map = {}
    for dish in ret:
        i = dish_map.setdefault(dish['name'], [])
        i.append(dish)
        dish_map[dish['name']] = i
    return dish_map

def list_orders():
    orders = json.loads(request(url + '/api/orders?type=json'))
    for order in orders:
        price = sum([int(i['price']) for i in order['order']])
        print 'username: ',order['name'].encode('utf-8'), price / 100
        for o in order['order']:
            print o['from'].encode('utf-8'), '-', o['name'].encode('utf-8'), 'x', o['number']
        print '-----'

if __name__ == '__main__':
    (options, args) = opt_parser.parse_args()
    read_config(options.config_file)
    login(ldap_user, ldap_pass)
    if options.list_orders:
        list_orders()
    if options.list_dishes:
        list_dishes(True)
    if options.new_order:
        orders = []
        for item in options.new_order.split(' '):
            price = -1
            if len(item.split(':')) == 3:
                name, price, count = item.split(':')
            elif len(item.split(':')) == 2:
                name, count = item.split(':')
            elif len(item.split(':')) == 4:
                shop, name, price, count = item.split(':')
                name = shop + name
            orders.append({'name': name, 'count': count, 'price': price})
        if do_order(orders):
            print 'OK'