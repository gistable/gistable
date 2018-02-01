'''
Copyright 2013 Pontiflex, Inc.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this work except in compliance with the License. You may obtain a copy of the License in the LICENSE file, or at:

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
'''

from bs4 import BeautifulSoup
import urllib2


def getBestPin(username):
	'''
	the get_pins method looks at a company (or user) pinterest page and
	scrapes their pins for the following metadata:

	* Pinterest Username, Account Description, Account Website, Account
	  Twitter, Profile Image URL
	* Pin URL
	* Image URL
	* Description
	* Repin Count
	* Likes Count

	get_pins then looks for the pin with the most repins, finds it's index, and
	collates the corresponding metadata into a simple python list.
	'''

	# Initilize the scrapping for a particular company's pins

	site = "http://pinterest.com/%s/pins/" %username

	hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
	       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
	       'Accept-Encoding': 'none',
	       'Accept-Language': 'en-US,en;q=0.8',
	       'Connection': 'keep-alive'}

	req = urllib2.Request(site, headers=hdr)

	try:
	    page = urllib2.urlopen(req)
	except urllib2.HTTPError, e:
	    print e.fp.read()

	content = page.read()

	soup = BeautifulSoup("".join(content))

	# Create a new empty list
	pinterest_list = []

	# Pinterest Profile Metadata
	n = soup.findAll('h1')
	pin_name = n[1].string
	pinterest_list.append(pin_name)

	d = soup.findAll('p', 'colormuted')
	profile_description = d[0].string
	pinterest_list.append(profile_description)

	z = soup.findAll('a', 'ProfileImage')
	profile_image_url = z[0].get('href')
	pinterest_list.append(profile_image_url)

	w = soup.findAll('a', 'colorless')
	website = w[0].get('href')
	pinterest_list.append(website)

	t = soup.findAll('a', 'twitter')
	twitter = t[0].get('href')
	pinterest_list.append(twitter)

	# Scrap Pin URLs into a list
	pin_url_list = []
	pin_url = soup.findAll("a", "PinImage")
	for i in pin_url:
	    pin_url_list.append(i.get('href'))

	# Scrape Image URLs into a list
	image_url_list = []
	image_url = soup.findAll("img", "PinImageImg")
	for i in image_url:
	    image_url_list.append(i.get('src'))

	# Scrape Image URLs into a list
	description_list = []
	description = soup.findAll("p", "description")
	for i in description:
		description_list.append(i.string)
	        
	# Scrape Repin Numbers
	repin_list = []
	repin = soup.findAll("span", "RepinsCount")
	for i in repin:
	    j = i.string
	    k = j.split()
	    repin_list.append(int(k[0]))

	# Scrape Like Numbers
	likes_list = []
	likes = soup.findAll("span", "LikesCount")
	for i in likes:
	    j = i.string
	    k = j.split()
	    likes_list.append(int(k[0]))

	# Find the index of the pin with the most repins
	most_repins = max(repin_list)
	index = repin_list.index(most_repins)

	# Fill empty list with corresponding indexed data
	pinterest_list.append(pin_url_list[index])
	pinterest_list.append(image_url_list[index])
	pinterest_list.append(description_list[index])
	pinterest_list.append(repin_list[index])
	pinterest_list.append(likes_list[index])

	# Return Pinterest data for Pin w/ most repins
	return pinterest_list