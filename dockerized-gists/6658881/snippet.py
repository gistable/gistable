#!/usr/bin/env python


'''
Query on GoogleImageSearch and install resulted images by scraping.

To use this script install mechanize and BeautifulSoup packages as
easy_install mechanize
easy_install Beautiful

Example Run:
installQueriedGoogleImages('spotty')

Eren Golge erengolge@gmail.com - www.erengolge.com - 17 April 2013
'''

import json
import pdb
import urllib
import mechanize 
import cookielib
import sys
import os
from BeautifulSoup import BeautifulSoup

def installQueriedGoogleImages(query):
	br = mechanize.Browser()
	cj = cookielib.LWPCookieJar()
	br.set_cookiejar(cj)
	
	# Browser options
	br.set_handle_equiv(True)
	br.set_handle_gzip(True)
	br.set_handle_redirect(True)
	br.set_handle_referer(True)
	br.set_handle_robots(False)
	
	# Follows refresh 0 but not hangs on refresh > 0
	br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
	
	# Want debugging messages?
	#br.set_debug_http(True)
	#br.set_debug_redirects(True)
	#br.set_debug_responses(True)
	
	# User-Agent (this is cheating, ok?)
	br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
	
	main_url = 'https://www.google.com.tr/search?q='+query+'&safe=off&client=ubuntu&hs=Hrw&channel=fs&biw=1317&bih=678&hl=en&um=1&ie=UTF-8&tbm=isch&source=og&sa=N&tab=wi'
	r = br.open(main_url)
	counter = 1
	for i in range(5):
		html = r.read()
		soup = BeautifulSoup(html)
		for link in br.links():
			if 'IMG' in link.text:
				r = br.open(link.url)
				html = r.read()
				soup2 = BeautifulSoup(html) # parse html
				links = soup2.findAll('a')
				for target in links:
					if 'Full-size image' in str(target.getString()):
						link_img = target['href']
						print 'Downloading image %d-%s -...\n'%(counter, link_img)
						try:
							#pdb.set_trace()
							ext = link_img[-4:]
							urllib.urlretrieve(link_img, query+'/image'+str(counter)+ext)
						except (IOError):
							print 'image %d cannot be downloaded because of server error!...'%counter
						except UnicodeError:
							print 'image %d cannot be downloaded because of naming of website!...'%counter
						counter += 1
		
		spans = soup.findAll('span')
		for next in spans:
			if 'Next' in str(next.getString()):
				link = next.parent
				link = link['href']
		r = br.open(link)

if __name__ == '__main__':
	color= sys.argv[1]

	if not os.path.exists(color):
		os.makedirs(color)

	
	installQueriedGoogleImages(color)
	