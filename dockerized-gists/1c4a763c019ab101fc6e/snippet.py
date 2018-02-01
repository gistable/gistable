'''
Created on Sep 19, 2013

@author: anuj
'''
# your code goes here
import re
import httplib
import urllib2
import robotparser
import time
from urlparse import urljoin
import BeautifulSoup
from urlparse import urlparse
import reppy
#from requests import requests

regex = re.compile(
         r'^(?:http|ftp)s?://' # http:// or https://
         r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
         r'localhost|' #localhost...
         r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
         r'(?::\d+)?' # optional port
         r'(?:/?|[/?]\S+)$', re.IGNORECASE)

def isurlvalid(url):
    return True;

def ishtmlcontent(pagecontent):
    t=pagecontent.info().getheader('Content-Type')
    if('text/html' in t):
        return True;
    return False

def remove_duplicates(l):
    return list(set(l))

def list_difference(l1,l2):
    return list(set(l1) - set(l2))

def add_pagetocrawl_list(page,crawled,cnt):
     crawled.append(page)
     print cnt
     print 'Crawled:'+page
     crawled=remove_duplicates(crawled)
     return crawled

def crawler(SeedUrl):
    tocrawl=[SeedUrl]
    crawled=[]
    cnt=0
    while tocrawl:
        page=tocrawl.pop(0)
        #time.sleep(5)
        hdr={'User-Agent':'htdig'}
        try:
            rp = robotparser.RobotFileParser()
            page_url = urlparse(page)
            base = page_url[0] + '://' + page_url[1]
            robots_url = urljoin(base, '/robots.txt')
            rp.set_url(robots_url)
            rp.read()
#             r=reppy.fetch()
        #    x = reppy.fetch(page+'/robots.txt')
            req = urllib2.Request(page, headers=hdr)         
            pagecontent=urllib2.urlopen(req)            
            if page not in crawled:
                s=pagecontent.read()  
                if (ishtmlcontent(pagecontent)):          
                    soup=BeautifulSoup(s)
                    links=soup.findAll('a',href=True)     
                    for l in links:
                        if (isurlvalid(l['href'])):
                            if rp.allowed('*', l['href']):
                                u1=urljoin(page,l['href'])
                                tocrawl.append(u1)
                    crawled.append(page)
                    cnt=cnt+1
                    print cnt
                    print 'Crawled:'+page
                    crawled=remove_duplicates(crawled)
                else:
                    if(page.endswith(".pdf")):
                        crawled.append(page)
                      #  print cnt
                        cnt=cnt+1
                        print 'Crawled:'+page
                        crawled=remove_duplicates(crawled)
            if(len(crawled)==100):
                    tocrawl=[]
        except Exception, err:
           # print Exception, err
            continue
    return crawled

start_time = time.time()
visitedurls=crawler('http://www.ccs.neu.edu')
print len(visitedurls)
for a in visitedurls:
    print a
print time.time() - start_time, "seconds"