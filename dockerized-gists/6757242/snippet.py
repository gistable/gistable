#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Usage:
  dayone-to-b3.py [options]

Options:
  -p, --path=<path> top directory of your blog. [default: .]
"""

from bucket3 import b3tools
import plistlib
import os
from docopt import docopt
import re
import unidecode
import shutil

def slugify(str):
    # Credit: http://stackoverflow.com/a/8366771
    str = unidecode.unidecode(str).lower()
    return re.sub(r'\W+','-',str)

DropBox = '/Users/vrypan/Dropbox/'

DayOne_dir = os.path.join(DropBox, 'Apps', 'Day One', 'Journal.dayone')

TEMPLATE = """---
title: >
 %s
date: %s
slug: %s
tags: %s
attached: %s
location: %s
weather: %s
---
%s
"""

args = docopt(__doc__)
conf = b3tools.conf_get(args['--path'])

for f in os.listdir(os.path.join(DayOne_dir, 'entries')):
    j = plistlib.readPlist(os.path.join(DayOne_dir, 'entries', f))
    if 'Tags' in j and 'blog' in j['Tags']:

        text_lines = j['Entry Text'].split('\n')
        title = text_lines[0]
        body = '\n'.join(text_lines[1:])
        slug = slugify(unicode(title))
        date = j['Creation Date']
        if 'Location' in j:
            location = "\n locality: %s\n country: %s\n place: %s\n long: %s\n lat: %s" % (
                j['Location']['Locality'],
                j['Location']['Country'],
                j['Location']['Place Name'],
                j['Location']['Longitude'],
                j['Location']['Latitude']
                )
        else:
            location = ""

        if 'Weather' in j:
            weather = "\n C: %s\n F: %s\n description: %s\n icon: %s" % (
                j['Weather']['Celsius'],
                j['Weather']['Fahrenheit'],
                j['Weather']['Description'],
                j['Weather']['IconName']
                )
        else:
            weather = ""

        tags = ', '.join(
            [t for t in j['Tags'] if t != 'blog' ]
            )
        
        image_path = os.path.join(DayOne_dir, 'photos', '%s.jpg' % j['UUID'])
        if os.path.isfile(image_path):
            image = '%s.jpg' % j['UUID']
            body = "![photo](%s)\n\n%s" % (image, body)
        else:
            image = ''

        post = TEMPLATE % (
            title,
            date,
            slug,
            tags,
            image,
            location,
            weather,
            body,
            )
        prefix = j['Creation Date'].strftime('%y%m%d')
        dirname = os.path.join(
            conf['root_dir'],
            'posts',
            'dayone',
            "%s-%s" % (prefix, slug)
            )
        filename = os.path.join(dirname, "%s-%s.%s" % (prefix, slug, 'md'))
        if not os.path.exists(dirname):
            os.mkdir(dirname)
            f = open(filename, 'w')
            f.write(post.encode('utf8'))
            f.close()
            print "Created %s." % filename
            if image:
                shutil.copy2(
                    image_path, 
                    dirname
                )
                print "Copied %s" % image
        else:
            print '%s already exists.' % dirname



