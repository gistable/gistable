#!/usr/bin/env python

import urllib2
import Image
import cStringIO

imgdata = urllib2.urlopen("http://www.google.co.jp/intl/ja_jp/images/logo.gif").read()
img = Image.open(cStringIO.StringIO(imgdata))
img.save("goog.png")
