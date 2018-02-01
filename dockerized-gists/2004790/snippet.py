#!/usr/bin/env python

import os
import urllib2
import time

START = 20000
MAX_NUMBER = 22000

def download(bid):
    print bid, "\n"

    path = "img/%d.gif" % bid
    if os.path.exists(path):
        return True

    try:
        resp = urllib2.urlopen("http://red.st-hatena.com/images/ad/%d_banner.gif" % bid)
    except urllib2.HTTPError: 
        return False

    with open(path, 'wb') as f:
        f.write(resp.read())
        return True

def wait(sec=1):
    time.sleep(sec)
    return True

def main():
    for i in range(START, MAX_NUMBER):
        download(i)
        wait()

def test():
    assert download(23860)
    assert wait()

if __name__ == '__main__':
    main()
