#!/usr/bin/env python
# A quick and dirty script to rename a pinboard.in tag.
# I'll probably update this become a proper command line app one day

import urllib2
import pinboard

pinuser = ""
pinpasswd = ""

p = pinboard.open(pinuser, pinpasswd)
# Enter in the tag information below
p.rename_tag(old="old-tag", new="new_tag")

print "Done!"
