#!/usr/bin/python3

import urllib3
import re

DOMAIN='www.nyaa.se'
PAGE='search'
CATS='0_0'
FILTER='0'

http = urllib3.PoolManager()

def search_url(term):
	return 'http://{0}/?page={1}&cats={2}&filter={3}&term={4}'\
		.format(DOMAIN, PAGE, CATS, FILTER, term.replace(' ', '+'))

def search(term):
	return http.request('GET', search_url(term))

def filter_torrents(page):
	return re.findall('tid=[0-9]*', page.data.decode('utf-8'))

def download_torrents(destination, tids):
	for x in set(tids):
		r = http.request('GET', 'http://{0}/?page=download&{1}'.format(DOMAIN, x))
		filename = r.headers['Content-Disposition'].split('"')[1]
		print(filename + '.... OK')
		with open(destination+filename, 'wb+') as f:
			f.write(r.data)
		

if __name__ == '__main__':
	with open('torrents.txt') as f:
		for t in f:
			download_torrents('/home/rodrigo/Downloads/',filter_torrents(search(t.strip())))

