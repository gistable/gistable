from gevent import monkey; monkey.patch_all()
import gevent
import gevent.greenlet
from functools import partial
from random import random

import urllib
import urllib2

def on_exception(fun, greenlet):
    """Receiver in case of an error
    """
    print "Oops! Restarting..."
    fun()
    

def fetch_url(url):
    """Fetch an URL, sleep for some time and repeat. Die occasionally to emulate failure
    """
    while True:
        r = random()
        if r < 0.3:
            print "Raising an exception!"
            raise Exception("Time to die :(")
        data = urllib2.urlopen(url).read()
        print "Fetched %s..." % url
        gevent.sleep(r)


def main(urls):
    gs = [gevent.spawn(fetch_url, url) for url in urls]
    x = [g.link_exception(partial(on_exception, partial(main, urls))) for g in gs]
    gevent.joinall(gs)


if __name__ == '__main__':
    print main(["http://google.co.il", "http://google.com"])
