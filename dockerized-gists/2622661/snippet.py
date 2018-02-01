#!/usr/bin/env python

import urllib2
import re

URL = "https://gist.github.com/jorgebastida/2622704/raw/b264cf36cace951cd1ab32c1a783c0c26ff28545/trash.txt"

print sum(map(int, re.sub("\D", "", urllib2.urlopen(URL).read())))