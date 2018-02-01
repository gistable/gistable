"""
This handy script will download all wallpapears from simpledesktops.com

Requirements
============
BeautifulSoup - http://www.crummy.com/software/BeautifulSoup/
Python-Requests - http://docs.python-requests.org/en/latest/index.html

Usage
=====
cd /path/to/the/script/
python simpledesktops.py
"""

from StringIO import StringIO
from bs4 import BeautifulSoup
import requests
import os

try:
	os.mkdir('walls')
except OSError:
	pass

page = 1
while True:
	page_request = requests.get('http://simpledesktops.com/browse/%s/' % page)
	if page_request.status_code != 200:
		print 'page %s does not exist' % page
		break
	html = BeautifulSoup(page_request.text)
	images = html.findAll('img')
	for image in images:
		img_src = image['src']
		if 'static.simpledesktops.com/desktops/' in img_src:
			full_size_img = img_src.replace('.295x184_q100.png', '')
			img_name = full_size_img.split('/')[-1]
			img_request = requests.get(full_size_img)
			img_buffer = StringIO(img_request.content)
			
			img_file = open('walls/%s' % img_name, 'wb')
			img_file.write(img_buffer.getvalue())
			img_file.close()
			print '%s downloaded' % img_name
	print '\n================'
	print 'page %s finished' % page
	print '================\n'
	page += 1