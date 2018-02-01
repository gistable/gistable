#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import sys
import urllib

from optparse import OptionParser

parser = OptionParser()
parser.add_option("-d", "--description", dest="description", default="Gist uploaded with gist.py https://gist.github.com/aseba/5198855", help="Description", metavar="DESC")
parser.add_option("-n", "--name", dest="name", help="File Name", default="", metavar="NAME")
parser.add_option("-p", "--private", action='store_false', dest="public", default=True, help="Set Gist as private")
parser.add_option("-o", "--open", action='store_true', dest="open", default=False, help="Open html url using command 'open' when finished")

(options, args) = parser.parse_args()

content = "\n".join([line for line in sys.stdin])

payload = { "description": options.description, "public": options.public, "files": { options.name: { "content": content } } }

url = 'https://api.github.com/gists'

raw_result = urllib.urlopen(url, json.dumps(payload))

try:
	result = json.loads(raw_result.read())
	if 'html_url' in result:
		if options.open:
			subprocess.call(['open', result['html_url']])
		else:
			print result['html_url']
	else:
		print result

except ValueError:
	print "Something went wrong when talking with github: ", sys.exc_info()[0]