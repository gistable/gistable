#!/usr/bin/env python2.7

''' Creates wordlists from web scraping. BeautifulSoup requierd (pip install beautifulsoup) '''
import sys
import os
import robotparser
from BeautifulSoup import BeautifulSoup as bs
import urllib2
from urlparse import urlparse

PATH = '/wordlist.txt'

visited =[]

''' Returns all links found on page'''
def return_links(raw_page):
	soup = bs(raw_page)
	links = []
	for link in soup.findAll('a'):
		links.append(link.get('href'))
	return links
	
''' Saves all words in source code seperated with whitespace to file (on PATH) with one word per row'''
def save_wordlist(raw_page):
	soup = bs(raw_page)
	wordlist = str.split(soup.__str__())
	f = open(PATH, 'a')
	for word in wordlist:
		f.write(word+'\n')
	f.close()

def recheck_robot(rp, up):
	rp.set_url(up.scheme +"://"+ up.netloc + "/robots.txt")
	rp.read()
	if verbose:
		print "Checking robot.txt on : "+ up.scheme +"://"+ up.netloc + "/robots.txt"
	
''' Recursive method that checks Robotparser if it is allowed to crawl and if allowed
 	it parses all word and make recursive call to all found URLs'''
def scrape(baseurl, page, rp):
	if page is None: 
		return 
	url = urlparse(page)
	if url.netloc=="":
		if baseurl[-1] != "/" and url.path != "" and url.path[0] != "/":
			baseurl = baseurl + "/"
		if url.path != "" and baseurl[-1] == "/" and url.path[0] == "/" :
			baseurl = baseurl[:-1]
			
		newurl = baseurl + url.path
		if "http" not in newurl: 
			newurl = "http://"+newurl
	else:
		if baseurl != url.netloc: 
			recheck_robot(rp, url)
			
		newurl = url.geturl()
		baseurl = url.netloc
		


	if newurl in visited:
		return
	
	visited.append(newurl)
	if rp.can_fetch("*", newurl):
		if verbose: 
			print "Allowed to fetch page "+newurl+". Initiating scrape."
		try:
			raw_page = urllib2.urlopen(newurl)
			raw_page = raw_page.read()
			#scrape for words. 
			save_wordlist(raw_page)

			# scrape for links. Foreach link scrape.
			links = return_links(raw_page)
			if not links:
				return
			for link in links:
				scrape(baseurl, link, rp)
		except (urllib2.URLError, urllib2.HTTPError, ValueError): 
			return
		

		
	else:
		if verbose: 
			print "Not allowed to fetch page "+baseurl+page+". Shutting down operations"
		return
			



if __name__ == "__main__":
	if len(sys.argv) == 1: 
		print "Call with 'python wordcollector.py [--verbose] [url]'"
		exit()
	if sys.argv[1] == '--verbose': 
		if len(sys.argv) == 2: 
			print "Call with 'python wordcollector.py [--verbose] [url]'"
			exit()
		verbose = True
		url = sys.argv[2]
	else: 
		verbose = False
		url =  sys.argv[1]

	if verbose : 
		print "URL: " + url
	up = urlparse(url)
	up.netloc
	if verbose:
		print "Reading " +up.scheme +"://"+ up.netloc +"/robots.txt"
	rp = robotparser.RobotFileParser()
	recheck_robot(rp, urlparse(url))
	if rp.can_fetch("*", url):
		if verbose: 
			print "Allowed to fetch root. Initiating reqursive scrape."
		# INITIATE RECURSIVE SCRAPE.
		try:
			scrape(url, "", rp)
		except KeyboardInterrupt: 
			pass
		if verbose:
			print""
			print "---------------------" 
			print "Scrape was completed."
			print "Number of words harvested:"
			os.system("wc -l " + PATH)
			print "---------------------" 
			 
	else:
		if verbose: 
			print "Not allowed to fetch root. Shutting down operations"
		exit()
	

