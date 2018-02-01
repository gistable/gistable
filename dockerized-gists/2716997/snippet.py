#!/usr/bin/python

"""
Random Python projects from GitHub.

The first one is a popular one from the Top 100.
The second one is from the rest. 
"""

import random
import urllib2
import json
import textwrap

MAX = 196
PAGE = random.randint(2, MAX)
URL_POP = 'http://github.com/api/v2/json/repos/search/python?language=Python'
URL_ALL = URL_POP + '&start_page={page}'.format(page=PAGE)
WIDTH = 78

def remove_non_ascii(text): 
    return ''.join(c for c in text if ord(c) < 128)

def process(r):
    print '{o}/{n}   (watchers: {w}, forks: {f}, updated: {u})'.format(o=r['owner'], 
                                                                       n=r['name'], 
                                                                       w=r['watchers'], 
                                                                       f=r['forks'],
                                                                       u=r['pushed'][:10])
    desc = '\n'.join(textwrap.wrap(remove_non_ascii(r['description']), WIDTH))
    print '{d}'.format(d=desc)
    print '{url}'.format(url=r['url']),
    if r.has_key('homepage') and r['homepage']:
        print '/  {hp}'.format(hp=r['homepage'])
    else:
        print
#    print 'fork: {f}'.format(f=r['fork'])

def choose_from(url):
    text = urllib2.urlopen(url).read()
    repos = json.loads(text)['repositories']
    repo = random.choice(repos)
    process(repo)

def main():
    choose_from(URL_POP)
    print '=========='
    choose_from(URL_ALL)
    
#############################################################################

if __name__ == "__main__":
    main()