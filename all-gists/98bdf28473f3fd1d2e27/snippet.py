#!/usr/bin/env python
# dump-images.py
#
# Extract all the image data from the banners and store them as separate images
# in a provided output directory.
#
# Example:
# shodan download --limit -1 screenshots.json.gz has_screenshot:true
# ./dump-images.py screenshots.json.gz images/

import shodan
import shodan.helpers as helpers

import os
import sys

# Usage
if len(sys.argv) != 3:
	print('Usage: {} <Shodan json.gz> <output directory>'.format(sys.argv[0]))
	sys.exit(-1)
	
input_file = sys.argv[1]
output_dir = sys.argv[2]

# Make sure the directory exists
if not os.path.exists(output_dir):
	os.mkdir(output_dir)

for banner in helpers.iterate_files(input_file):
	# Try to grab the screenshot from the banner
	screenshot = helpers.get_screenshot(banner)
	
	# If we found a screenshot then create a file w/ the data
	if screenshot:
		# Create the file handle
		image = open('{}/{}.jpg'.format(output_dir, banner['ip_str']), 'w')
		
		# Write the image data which is stored using base64 encoding
		image.write(screenshot['data'].decode('base64'))
