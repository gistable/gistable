#!/usr/bin/env python
"""
kc.py - jenni's Kaltura Knowledge Center Search Module
author Zohar Babin <zohar.babin@kaltura.com>
http://www.zoharbabin.com/kaltura-knowledge-center-search-irc-bot-module
Copyright Kaltura Inc. 
Licensed under AGPL v3.

More info:
 Returns the list of search results from the first page in the Kaltura Knowledge Center (http://knowledge.kaltura.com)
 * jenni: https://github.com/myano/jenni/
"""

import re
import mechanize
import sys
import string
from bs4 import BeautifulSoup
import bitly_api
import urllib

def kc(jenni, input):
    # We use bitly to shorten the Urls.. this is not a must, but makes the IRC messages cleaner
    # Get your bitly API token from: https://bitly.com/a/oauth_apps
    bitly = bitly_api.Connection(access_token="REPLACE_THIS_WITH_YOUR_BITLY_TOKEN")
    
    # phenny keeps the command input in input.group(2). input.group(1) would be the command itself (kc in our case)
    input_txt = urllib.quote(input.group(2).encode('utf-8'))
    
    # give the user some feedback while we go searching...
    jenni.reply("Searcing the Kaltura Knowledge Center (knowledge.kaltura.com) for: "+input.group(2))
    jenni.reply("If I find any results for your search, I will return all the results from the first page.")
    
    # we use mechanize for fetching the search results page
    br = mechanize.Browser()
    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)
    # Follows refresh 0 but not hangs on refresh > 0
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
    # User-Agent (this is cheating, ok?)
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
    
    br.open("http://knowledge.kaltura.com/search/"+input_txt)
    assert br.viewing_html()
    html = br.response().read()
    soup = BeautifulSoup(html, "lxml") #lxml is the faster parser of all

    search_div = soup.findAll("div", class_="search-results") #get the search-results div
    
    # if we couldn't find any results for the desired terms:
    if len(search_div) == 0:
        return jenni.reply("I couldn't find any results for your search of "+input_txt)
    
    # If resulsts were indeed found, parse the page for all h2 headers in the search-results div
    # and return all the links to the results
    rx = re.compile('\W+') #this will be used to cleanup any non textual chars from the result title
    counter = 1
    # we will only have one search div
    for div in search_div:
        headers = div.findAll("h2")
        # every search result in the KC is under <article><h2>.. so we fetch all h2
        for h in headers:
            links = h.findAll("a")
            for a in links:
                # every h2 will have 2 links, one that is used to hide/show the description and one linking to the result page
                # ignore the links that are empty (used to hide/show desc box)
                if a["href"] != "#":
                    #cleanup the title:
                    tmpTitle = a["title"].encode('ascii', 'ignore')
                    titleTxt = rx.sub(' ', tmpTitle.strip())
                    #shorten the url:
                    bitlyUrl = bitly.shorten("http://knowledge.kaltura.com"+str(a['href']))
                    #print a result to the user:
                    jenni.reply(str(counter)+") "+titleTxt+" - "+bitlyUrl["url"])
                    counter += 1
#defines the command used to call this module:
kc.commands = ['kc']
#set this to how important you feel this module should be treated among other modules (low/medium/high):
kc.priority = 'high'
#description text for help
kc.example = '.kc [any kaltura search term]'

if __name__ == '__main__':
    print __doc__.strip()