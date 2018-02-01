#!/usr/bin/env python
import urllib
import sys
import json
from mwlib import parser
from mwlib.refine import compat

if __name__ == "__main__":
	params = urllib.urlencode({
		"format": "json",
		"action": "query",
		"prop": "revisions",
		"rvprop": "content",
		"titles": "ISO_3166-1",
		"rvsection": "4",
	})
	wc = urllib.urlopen("http://en.wikipedia.org/w/api.php?%s" % params)
	if wc.getcode() != 200:
		print "Fail!"
		sys.exit(2)

	raw = wc.read()
	rdata = json.loads(raw)
	wc.close()

	page = rdata['query']['pages'].itervalues().next()
	if not page:
		print "NO page found"
		sys.exit(3)

	revision = page['revisions'][0]
	if not revision:
		print "NO revision found"
		sys.exit(4)

	content = revision[str(revision.keys()[0])]
	parsed = compat.parse_txt(content)
	table = parsed.find(parser.Table)[0]

	if not table:
		print "Table not found"
		sys.exit(5)

	for row in table.children:
		cells = row.find(parser.Cell)
		print cells[0].asText().replace("}}", "").replace("{{", "").strip() + \
		" || " + cells[1].asText().strip() + " || " + cells[2].asText().strip() \
		+ " || " + cells[3].asText().strip()
