#!/usr/bin/env python
# -*- coding: utf8 -*-
# author: amoblin <amoblin@163.com>

import sys, re, urllib2, os, urllib

beauty_url = "http://huaban.com/favorite/beauty/"
#beauty_url = "http://huaban.com/"
pin_re = '<a href="/pins/(.+?)/"'

def get_img_url(pin):
    pin_url = "http://huaban.com/pins/%s/" % pin
    print "pin_url: %s" % pin_url
    img_url_re = '<img alt=".+?" src="(.+?)"'
    pg = urllib2.urlopen(pin_url)
    content = pg.read()
    pg.close()
    try:
        img_url = re.findall(img_url_re, content)[0]
    except:
        print re.findall(img_url_re, content)
        sys.exit(1)
    print img_url
    return img_url

if __name__ == "__main__":
    if len(sys.argv) < 2:
        local_path = "./huaban"
    else:
        local_path = sys.argv[1]

    if not os.path.exists(local_path):
        try:
            os.makedirs(local_path)
        except e:
            print e
            sys.exit(1)

    print "pin images will saved to: %s" % local_path

    os.system("curl -s %s -o /tmp/huaban.html" % beauty_url)
    content = open("/tmp/huaban.html").read()

    pins = re.findall(pin_re, content)[1:]
    for pin in pins:
        img_url = get_img_url(pin)
        print "saving pin: %s" % pin
        urllib.urlretrieve(img_url, "%s/%s.jpeg" % (local_path, pin))