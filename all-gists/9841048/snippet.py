# -*- coding:utf-8 -*-
#                                  _        _                    _
#                                 | |      | |                  | |
#    ___   ___   _   _  _ __    __| |  ___ | |  ___   _   _   __| |
#   / __| / _ \ | | | || '_ \  / _` | / __|| | / _ \ | | | | / _` |
#   \__ \| (_) || |_| || | | || (_| || (__ | || (_) || |_| || (_| |
#   |___/ \___/  \__,_||_| |_| \__,_| \___||_| \___/  \__,_| \__,_|
#Creative Commons Attribution-ShareAlike 4.0 International License.
import re
import urllib2
__author__ = 'lupettohf'
__version__ = '1.0'
#re
audior = '(?<="streamUrl":").+\?s'
# Download page source
url = raw_input("Soundcloud link:")
down = urllib2.urlopen(url)
data= down.read()
# Parse link
audiofile = re.compile(audior).search (data)
# Save as
name = raw_input("Save as:")
# Download and save
print("Downloading %s.mp3" %name)
with open(name + ".mp3",'wb') as x:
    x.write(urllib2.urlopen(audiofile.group(0)).read())
    x.close()