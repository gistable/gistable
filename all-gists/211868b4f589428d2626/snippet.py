#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import json
import urllib
import urllib2
from dateutil.parser import parse

USERNAME = "mail@gmail.com"
PASSWORD = "superpass"


def request(url):
    # Digest Authentication
    authhandler = urllib2.HTTPDigestAuthHandler()
    authhandler.add_password('Application', url, USERNAME, PASSWORD)
    opener = urllib2.build_opener(authhandler)
    opener.addheaders = [('Accept', 'application/json')]
    urllib2.install_opener(opener)

    response = urllib2.urlopen(url)
    if response.getcode() == 200:
        body = json.loads(response.read())
        if len(body):
            return body

    return False


def download(url, created_at):
    if not url:
        return False

    try:
        print 'Source: %s' % url
        filename = url.split('/')[-1]
        filename = urllib.unquote(filename.encode('utf-8')).decode('utf-8')

        # if a file exists add created_at
        if os.path.isfile(filename):
            filename = '%s-%s' % (created_at, filename)

        print 'Downloading... %s' % filename
        urllib.urlretrieve(url, filename)
        os.utime(filename, (created_at, created_at))
    except IOError:
        download(url)
    except LookupError:
        pass


if __name__ == "__main__":
    page = 0
    result = True
    while result:
        page = page + 1
        result = request('http://my.cl.ly/items?per_page=100&page=' + str(page))

        if not result:
            break

        for n in result:
            source_url = n.get(u'source_url')
            created_at = int(time.mktime(parse(n.get(u'updated_at')).timetuple()))
            # print json.dumps(n, sort_keys=True, indent=4)
            download(source_url, created_at)
