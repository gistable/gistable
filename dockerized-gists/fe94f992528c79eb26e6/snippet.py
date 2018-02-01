import requests
from BeautifulSoup import BeautifulSoup as BS
import re

def get_dl_page(package_id):
	get_request = requests.get('https://apkpure.com/search?q=' + package_id)
	page = BS(get_request.text)
	# it is assumed that the first search result is the thing we are looking for
	link_ps = page.findAll('p', {'class': 'search-title'})
	page_link = link_ps[0].a.get('href')
	return 'https://apkpure.com' + page_link


def get_dl_link(page_link):
	get_request = requests.get(page_link)
	page = BS(get_request.text)
	# it is assumed that the first search result is the thing we are looking for
	link_ps = page.find('div', {"id": 'faq_box'}).findAll('a', {'ga': re.compile('download.*')})
	return link_ps[0].get('href')

print get_dl_link(get_dl_page('your.package.id.goes.here'))