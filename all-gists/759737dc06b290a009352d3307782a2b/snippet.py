# iceportal.py - download all available audio books from DB ICE Portal

import os
import json
import urllib
import urlparse
import contextlib

BASE = 'http://portal.imice.de/api1/rs/'

def load_json(url, verbose=True):
    if verbose:
        print(url)
    with contextlib.closing(urllib.urlopen(url)) as fd:
        doc = json.load(fd)
    return doc

def get_page(href, base=urlparse.urljoin(BASE, 'pages/')):
    url = urlparse.urljoin(base, href.lstrip('/'))
    return load_json(url)

def get_nav(name, url=urlparse.urljoin(BASE, 'navigation')):
    doc = load_json(url)
    return next(n['href'] for n in doc['main'] if n['linktext'].strip() == name)

def iteritems(href):
    page = get_page(href)
    for t in page['teasersMain']['items']:
        yield t['navigation']['href'], t['title']

def retrieve(source, target, base=urlparse.urljoin(BASE, 'audiobooks/path/')):
    sheet = urlparse.urljoin(base, source.lstrip('/'))
    path = load_json(sheet)['path']
    url = urlparse.urljoin(base, path)
    urllib.urlretrieve(url, filename=target)

audiobooks = get_nav(u'H\xf6rb\xfccher & H\xf6rspiele')
for href, title in iteritems(audiobooks):
    print('\n%s' % title)
    page = get_page(href)
    dirname = page['intro']['pageTitle']
    dirname = dirname.replace('.', '_').partition(':')[0]  # fix invalid
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    paths = [p['path'] for p in page['modules']['playlist']]
    for url in paths:
        target = os.path.join(dirname, url.rpartition('/')[2])
        if not os.path.exists(target):
            retrieve(url, target)
