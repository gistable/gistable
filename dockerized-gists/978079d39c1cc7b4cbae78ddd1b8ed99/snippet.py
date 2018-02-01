#!/usr/bin/python2.7
"""
Creates an RSS feed with DBLP JSON data from its API. 
Meant to be used as CGI script but can also be used as command-line.
Feedback and pull request welcome.
Martin Monperrus
March 2016
Licence: public domain
"""

import feedgenerator
import re
import urllib2
import os
import cgi
import re
import json
import sys
import codecs
import io


query_data = cgi.FieldStorage()

searchexp = "repair"
if "search" in query_data:
  searchexp = unicode(query_data['search'].value, 'utf8')

url = "http://dblp.org/search/publ/api/?q="+searchexp+"&h=1000&c=0&f=0&format=json&rd=1a"

print "Content-type: application/rss+xml"
#print "Content-type: text/plain"
print ""
#print url

response = urllib2.urlopen(url)
doc = response.read()
title="DBLP results on "+searchexp

feed = feedgenerator.Rss201rev2Feed(title=title,
        link=url,
        description=title,
        language="en")

ls = json.loads(doc)["result"]["hits"]["hit"]
# sorted is now handled by API parameter rd=1a
#ls = sorted(,key=(lambda x: x["info"]["year"]), reverse=True)

for i in ls:
      title=i["info"]["title"]
      if "authors" not in i["info"]: i["info"]["authors"]={"author":[]}
      if type(i["info"]["authors"]["author"])==unicode: i["info"]["authors"]["author"]=[i["info"]["authors"]["author"]]

      feed.add_item(
        title=title,
        link=i["info"]["url"],
        description=title+" | "+", ".join(i["info"]["authors"]["author"])+" | "+(i["info"]["venue"] if 'venue' in i["info"] else "")+" | "+i["info"]["year"],
        unique_id=i["info"]["url"]
      )
print feed.writeString('utf-8')
                 
  
