from __future__ import with_statement # we'll use this later, has to be here
from argparse import ArgumentParser

import requests
from BeautifulSoup import BeautifulStoneSoup as Soup

def parse_sitemap(url):
	resp = requests.get(url)
	
	# we didn't get a valid response, bail
	if 200 != resp.status_code:
		return False
	
	# BeautifulStoneSoup to parse the document
	soup = Soup(resp.content)
	
	# find all the <url> tags in the document
	urls = soup.findAll('url')
	
	# no urls? bail
	if not urls:
		return False
	
	# storage for later...
	out = []
	
	#extract what we need from the url
	for u in urls:
		loc = u.find('loc').string
		prio = u.find('priority').string
		change = u.find('changefreq').string
		last = u.find('lastmod').string
		out.append([loc, prio, change, last])
	return out

if __name__ == '__main__':
	options = ArgumentParser()
	options.add_argument('-u', '--url', action='store', dest='url', help='The file contain one url per line')
	options.add_argument('-o', '--output', action='store', dest='out', default='out.txt', help='Where you would like to save the data')
	args = options.parse_args()
	urls = parse_sitemap(args.url)
	if not urls:
		print 'There was an error!'
	with open(args.out, 'w') as out:
		for u in urls:
			out.write('\t'.join([i.encode('utf-8') for i in u]) + '\n')