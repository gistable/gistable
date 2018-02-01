#Retrive old website from Google Cache. Optimized with sleep time, and avoid 504 error (Google block Ip send many request).
#Programmer: Kien Nguyen - QTPros http://qtpros.info/kiennguyen
#change search_site and search_term to match your requirement
#Original: http://www.guyrutenberg.com/2008/10/02/retrieving-googles-cache-for-a-whole-website/


#!/usr/bin/python
import urllib, urllib2
import re
import socket
import os, errno, os.path
import time
import random, math
#import MySQLdb
import imp;

socket.setdefaulttimeout(30)
#adjust the site here
search_site="qtpros.info"
search_term="site:" + search_site

#mysql = imp.load_source("MySQLConnector", "mysql.py").MySQLConnector()
#mysql.connect('localhost','root','','webscrape',True)


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else: raise


def main():
    headers = {'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686 (x86_64); en-US; rv:1.8.1.4) Gecko/20070515 Firefox/2.0.0.4'}
    url = "http://www.google.com/search?q="+search_term

    regex_cache = re.compile(r'<a href="([^"]*)"[^>]*>Cached</a>')
    regex_next = re.compile('<a href="([^"]*)"[^>]*><span[^>]*>[^<]*</span><span[^>]*>Next</span></a>')
    regex_url = re.compile(r'search\?q=cache:[\d\w-]+:([^%]*)')
#    regex_title = re.compile('<title>([\w\W]+)</title>')
#    regex_time = re.compile('page as it appeared on ([\d\w\s:]+)')
    regex_pagenum = re.compile('<a href="([^"]*)"[^>]*><span[^>]*>[^<]*</span>([\d]+)')

    #this is the directory we will save files to
    mkdir_p(search_site)
    path = os.path.dirname(os.path.abspath(__file__)) + '\\' + search_site
#    path = os.path.dirname(os.path.abspath(__file__))
    counter = 0
    pagenum = int(math.floor(len([name for name in os.listdir(path)]) / 10) + 1)
    max_goto = 0;
    more = True
    if (pagenum > 1):
        while (max_goto < pagenum):
            req = urllib2.Request(url, None, headers)
            page = urllib2.urlopen(req).read()
            goto = regex_pagenum.findall(page)
#            print goto
            for goto_url, goto_pagenum in goto:
                goto_pagenum = int(goto_pagenum)
                if (goto_pagenum == pagenum):
                    url = "http://www.google.com" + goto_url.replace('&amp;', '&')
                    max_goto = pagenum
                    break
                elif (goto_pagenum < pagenum and max_goto < goto_pagenum):
                    max_goto = goto_pagenum
                    url = "http://www.google.com" + goto_url.replace('&amp;', '&')
            random_interval = random.randrange(5, 20, 1)
            print "sleeping for: " + str(random_interval) + " seconds"
            print "going to page: " + str(max_goto)
            print url
            time.sleep(random_interval)


    while(more):
        #Send search request to google with pre-defined headers
        req = urllib2.Request(url, None, headers)
        #open the response page
        page = urllib2.urlopen(req).read()
        #find all cache in the page
        matches = regex_cache.findall(page)
        #loop through the matches
        for match in matches:
            counter+=1
            #find the url of the page cached by google
            the_url = regex_url.findall(match)
            the_url = the_url[0]
            the_url = the_url.replace('http://', '')
            the_url = the_url.strip('/')
            the_url = the_url.replace('/', '-')
            #if href doesn't start with http insert http before
            if not match.startswith("http"):
                match = "http:" + match
            if (not the_url.endswith('html')):
                the_url = the_url + ".html"
            #if filename "$url"[.html] does not exists
            if not os.path.exists(search_site + "/" + the_url):
                tmp_req = urllib2.Request(match.replace('&amp;', '&'), None, headers)
                try:
                    tmp_page = urllib2.urlopen(tmp_req).read()
                    f = open(search_site + "/" + the_url, 'w')
                    f.write(tmp_page)
                    f.close()
                    print counter, ": " + the_url
                    #comment out the code below if you expect to crawl less than 50 pages
                    random_interval = random.randrange(15, 20, 1)
                    print "sleeping for: " + str(random_interval) + " seconds"
                    time.sleep(random_interval)
                except urllib2.HTTPError, e:
                    print 'Error code: ', e.code
                    pass
        #now check if there is more pages
        match = regex_next.search(page)
        if match == None:
            more = False
        else:
            url = "http://www.google.com"+match.group(1).replace('&amp;', '&')

if __name__=="__main__":
    main()