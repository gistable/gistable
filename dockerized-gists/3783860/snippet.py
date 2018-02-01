#!/usr/bin/env python

import sys
from urllib import urlencode

param = '%clipboard'.strip()
rooturl = "http://lmgtfy.com/?"
try:
	qs = urlencode({'q':param})
except:
	qs = ''
finally:
	sys.stdout.write("%s%s" % (rooturl, qs))