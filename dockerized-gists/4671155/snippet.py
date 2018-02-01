#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, re
import itertools
from functools import wraps
from pyquery import PyQuery as pq

class scrape:
  
    _scrape_routes = {}
    _scrape_tags = {}

    def __init__(self, ctx=None):
        self._ctx = ctx

    @staticmethod
    def route(route):
    
        def inner(f):
            def wrapped(*args, **kwargs):
              return f(*args, **kwargs)
            wrapped = wraps(f)(wrapped)          
            if isinstance(route, list):
                for r in route:
                    scrape._scrape_routes[r] = wrapped
            else:
                scrape._scrape_routes[route] = wrapped              
            return wrapped
        return inner
  
    @staticmethod
    def tag(self, tag):
        def inner(f):
            def wrapped(*args, **kwargs):
                return f(*args, **kwargs)
            wrapped = wraps(f)(wrapped)
            scrape._scrape_tags[tag] = wrapped
            return wrapped
        return inner
          
    def nav(self, url, tag=None):
        if tag is not None:
            for tag_i in scrape._scrape_tags.iterkeys():
                if tag == tag_i:
                    f = scrape._scrape_tags[tag]
                    d = pq(url=url)
                    return list(f(self._ctx, url, d))
                  
            return []
      
        else:
            for pat in scrape._scrape_routes.iterkeys():
                if re.search(pat, url):
                    f = scrape._scrape_routes[pat]
                    d = pq(url=url)
                    return list(f(self._ctx, url, d))
                  
            return []
 
        
class NewComics:
    
    def __init__(self):
        self.pages = None
    
    @scrape.route('/newreleases')
    def weekly(self, url, d):
        
        # save the total number of pages
        if self.pages is None:
            page_links = d('#resultstab .nav-search:first-child .paginate:first-child li a')          
            last_page = pq(page_links[-1]).text()            
            self.pages = int(last_page)
        
        for el in d('div.search-results div.title'):
            yield pq(el).text()
            
    
def main():    

    # setup our routes
    # saving some state when needed
    nc = NewComics()
    url = r'http://www.mycomicshop.com/newreleases?dw=0&p={0}'
    
    # get a navigator with a context object
    nav = scrape(nc).nav    
    
    for title in nav(url.format('1')):
        print title
    
    if 1 < nc.pages:
        for p in range(2, nc.pages + 1):
            for title in nav(url.format(p)):
                print title
    
    
if __name__ == "__main__":
    main()
