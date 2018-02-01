"""
This script requires the following Packages

  1: Twitter: https://pypi.python.org/pypi/twitter
  2: PyQuery: https://pypi.python.org/pypi/pyquery
  3: Jinja2: https://pypi.python.org/pypi/Jinja2
  
It's fairly primitive but works. It uses a Jinja2 template to create an OPML
file from the RSS feeds of the websites run by the people you follow on
Twitter.

It's pretty slow as it has to make an individual call to Twitter for each
URL, then call out to the website mentioned in the user's profile to find
an RSS feed.

To run it, create an app at https://dev.twitter.com/ and use the
consumer key and secret along with your own user's key and secret
(also generated when you create tha app). You only need read access.

Fill in those details below, and then run::

    python twopy.py > feeds.opml

After a few minutes you'll have an OPML file which you can import
into an app like Feedly.

Steadman
http://steadman.io/
"""

from twitter import Twitter, OAuth
from pyquery import PyQuery
from urllib import urlopen
from urlparse import urljoin
from jinja2 import Template
from logging import getLogger
from sys import stdout

TOKEN_KEY = ''
TOKEN_SECRET = ''
CONSUMER_KEY = ''
CONSUMER_SECRET = ''

t = Twitter(auth = OAuth(TOKEN_KEY, TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET))
logger = getLogger()

TEMPLATE = """<?xml version="1.0" encoding="ISO-8859-1"?>
<opml version="1.0">
	<head>
		<title>OPML</title>
		<ownerName>Steadman</ownerName>
		<ownerEmail>mark@steadman.io</ownerEmail>
	</head>
	<body>
		{% for f in feeds %}<outline text="{{ f.name }}" title="{{ f.name }}">
			<outline text="{{ f.name }}" title="{{ f.name }}" type="rss" xmlUrl="{{ f.feed_url }}" htmlUrl="{{ f.html_url }}" />
		</outline>
		{% endfor %}
	</body>
</opml>"""

template = Template(TEMPLATE)
feeds = []

for id in t.friends.ids().get('ids'):
	try:
		u = t.users.show(id = id)
	except:
		continue
	
	if 'url' in u:
		if not u['url']:
			continue
		
		try:
			r = urlopen(u['url'])
		except:
			continue
		
		p = PyQuery(r.read())
		for m in p('head').find('link'):
			if m.attrib.get('type') == 'application/rss+xml':
				feeds.append(
					{
						'name': u['name'],
						'feed_url': urljoin(r.url, m.attrib.get('href')),
						'html_url': r.url
					}
				)
				
				logger.info(
					urljoin(
						r.url,
						m.attrib.get('href')
					)
				)
				
				break

stdout.write(
	template.render(feeds = feeds)
)