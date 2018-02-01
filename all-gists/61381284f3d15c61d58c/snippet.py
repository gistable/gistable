#!/usr/bin/python
from urllib2 import *
from json import *

title = raw_input("Search: ")

#replaces space with %20(character used for space in url)
title = title.replace(" ", "%20")

#adding title to request
url = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles="+title+"&redirects="

try:
    #the required data is in {query:{pages{pageid{extract}}}}
    data = urlopen(url)
    jobject = load(data)
    query = jobject['query']
    pages = query['pages']
    for i in pages:
        abc = pages[i]
    summary = abc['extract']
    topic = abc['title']

    print (topic+":")
    print(summary)
except:
    print("Search did not matched OR could not connect")


