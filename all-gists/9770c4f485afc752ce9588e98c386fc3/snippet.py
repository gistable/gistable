#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author:      Asbra
# @date:        2014-12-12
# @modified_by: Asbra
# @modified_at: 2014-12-12
# Saves images & webm from Anon-IB
# Usage: anonib section thread path
# section - eg. 'red' for reddit (/red/)
# thread - thread No.
# path - path on disk (relative to script) to save files in

import re        # Regular expressions
import requests  # To make HTTP requests
import shutil    # Used when downloading file
import os        # For creating folders


class anonib(object):

    def __init__(self):
        return

    def thread(self, section, id):
        # Build Url
        url = 'https://anon-ib.su/' + section + '/res/' + id + '.html'

        # Download page
        r = requests.get(url)

        # Error handling
        if r.status_code != 200 or not r.content:
            return []

        # Find all images in thread
        rx = re.compile(r'href=".*?(\/' + section + '\/src\/[0-9]+(?:-[0-9]+)?\.(jpe?g|png|gif|web(?:m|p)))"')
        m = rx.findall(r.content)

        images = []

        for i in m:
            images.append(i[0])

        return self.uniq(images)

    # Remove duplicate elements in list
    def uniq(self, seq):
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))]


if __name__ == '__main__':
    import sys

    section = sys.argv[1]
    thread = sys.argv[2]
    path = sys.argv[3].rstrip('/') + '/'

    if not os.path.isdir(path):
        os.mkdir(path)

    chan = anonib()

    images = chan.thread(section, thread)

    for image in images:
        match = re.findall(r'/([0-9]+(?:-[0-9]+)?\.(jpe?g|png|gif|web(?:m|p)))$', image)

        if not match or not match[0] or not match[0][0]:
            print image
            continue

        filename = path + match[0][0]

        if not os.path.isfile(filename):
            q = requests.get('https://anon-ib.su' + image, stream=True)

            with open(filename, 'wb') as f:
                q.raw.decode_content = True
                shutil.copyfileobj(q.raw, f)
                print filename
