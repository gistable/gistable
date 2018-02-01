#!/usr/bin/env python
#
# Copyright 2011, Jason Graham
#
# Uses python-markdown to convert a markdown document to the body
# of an HTML document to display with cgit (http://hjemli.net/git/cgit/).
#
# Install:
#
# 1- Install python-markdown ( sudo apt-get install python-markdown )
# 2- Copy this script to /usr/local/bin/markdownize_cgit.py (with exec rights)
# 3- Add this statement into the your cgit configuration:
#      # Implement globally
#      about-filter=/usr/local/bin/markdownize_cgit.py
#
#      OR
#
#      # Implement On a per-repo basis (must use
#      # the enable-filter-overrides=1 option)
#      repo.about-filter=/usr/local/bin/markdownize_cgit.py
#

import sys
import markdown

def markdownize(in_stream=None, out_stream=None):
	# If not provided in_stream will be read from stdin and out_stream 
	# will be written to stdout.
	if in_stream is None:
	    in_stream = sys.stdin
	if out_stream is None:
	    out_stream = sys.stdout

	out_stream.write(markdown.markdown(in_stream.read()))

if __name__ == '__main__':
	if len(sys.argv) != 1:
	    sys.exit(1)
	markdownize()