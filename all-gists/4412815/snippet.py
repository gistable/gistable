#!/usr/bin/python

# This script is a replacement for the OS X "say" command.
# Built on a Raspberry Pi :)
# to install:
# sudo apt-get install curl mpg123
# sudo curl https://gist.github.com/raw/4412815 > say; chmod a+x say; sudo mv say /usr/bin/
# say hello world

import subprocess
import urllib2
from sys import argv

args = [ urllib2.quote(x) for x in argv[1:] ]
param_s = '+'.join(args)

url = "http://translate.google.com/translate_tts?ie=UTF-8&tl=en&q=%s" % param_s
cmd = "curl '%s' -s --user-agent 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1)' | mpg123 -q -" % url
subprocess.call(cmd, shell=True)