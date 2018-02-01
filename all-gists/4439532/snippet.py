#! /usr/bin/python
"""
brute force get title of web page
usage: getTitle.py url
Gordon Meyer January 1, 2013 
www.gordonmeyer.com
"""

# modules used
import urllib2, urlparse, string, os

def getPage(theURL):
  ## returns the HTML text of the URL
	req = urllib2.Request(theURL)
	thePage = urllib2.urlopen(req)
	theHTML = thePage.read()
	
	return theHTML
##
def extractTitle(theLine):
	## finds and returns contents of <title> tag
	titleStart = theLine.find("<title>")
	if titleStart > -1: #make sure we found the tag, -1 will mean we did not
		titleStart = titleStart + 7 #skip to end of tag
		titleEnd = theLine.find("</title>")
		theTitle = theLine[titleStart:titleEnd]
		theTitle = theTitle.strip() # remove whitespace
	else:
		theTitle = ""
		
	return(theTitle)



## MAIN

# get URL from Keyboard Maestro variable
theURL = os.getenv('KMVAR_theURL')
thePageHTML = getPage(theURL)
theTitle = extractTitle(thePageHTML)
print theTitle
