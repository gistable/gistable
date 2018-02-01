#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import errno
from string import Template
from slugify import slugify
from xml.dom.minidom import parse

"""
With the great help of Florent Matignon, a script that exports
all my preciously saved Google Reader XML export to my new Jekyll
blog.

Victor Perron 2013
"""


POST_TEMPLATE = """\
---
layout: post 
title: ${title}
date: ${date}
---

${content}

"""


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

class Post(object):

    def __init__(self, entry):
        self.entry = entry

    def extract(self, tagName, elem=None):
        obj = self.entry
        if elem is not None:
            obj = elem
        return obj.getElementsByTagName(tagName)[0].childNodes[0].data

    def author(self):
        container = self.entry.getElementsByTagName('author')[0]
        return self.extract('name', container)

    def content(self):
        return self.extract('content')

    def title(self):
        return self.extract('title')

    def date(self):
        return self.extract('published')


def utfWrite(s):
    sys.stdout.write(s.encode('utf8'))

def main():
    filename = sys.argv[1]
    basename = os.path.splitext(filename)[0]
    mkdir_p(basename)
    dom = parse(filename)
    entries = dom.getElementsByTagName('entry')
    for entry in entries:
        post = Post(entry)
        out_filename = os.path.join(basename, post.date()[:10]+'-'+slugify(post.title())+'.html')
        params = {
            'date': post.date(),
            'title': post.title(),
            'author': post.author(),
            'content': post.content(),
        }
        txt = Template(POST_TEMPLATE).safe_substitute(params)
        with open(out_filename, 'w') as f:
            f.write(txt.encode('utf-8'))

if __name__ == "__main__":
    main()