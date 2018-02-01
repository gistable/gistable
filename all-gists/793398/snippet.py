#!/usr/bin/env python
# -*- coding: utf8 -*-
from flask import Flask, redirect, url_for
from markdown import markdown
import os
import re


# create the app
# TODO: load config/template from files, with fallbacks
app = Flask(__name__)
root_dir = os.path.expanduser('~/Text')
template = """
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8" />
	<title>%s | Brainerd</title>
	<style>
		body { padding: 0; margin: 0; }
		header { padding: 1em; background: royalblue; color: white; }
		#container { width: 650px; margin: 0 auto; }
		#content { padding: 1em; }
	</style>
</head>
<body>
<div id="container">
	<header>
		<p>Brainerd wiki system</p>
		<h1>%s</h1>
	</header>
	<div id="content">
		%s
	</div>
</div>
</body>
</html>
"""


@app.route("/")
@app.route("/w/")
def homepage():
	# TODO: make this a directory listing of root_dir
	return "Hello there."
	
	
@app.route("/w/<path:page>")
def wiki(page):
	# reformat the URL - space becomes hyphen
	# also, strip out path injection attacks
	# TODO: substitute back in the spaces, somehow
	new_page = page.replace(" ", "-")
	new_page = re.sub(r"\.+/", "", new_page)
	if new_page is not page:
		return redirect(url_for("wiki", page=new_page))
		
	# render file or directory
	# TODO: directory listings, non–Markdown files, catch Markdown errors
	file_path = "%s/%s.mdown" % (root_dir, page)
	if os.path.isfile(file_path):
		try:
			with open(file_path, 'r') as f:
				return template % (page, page, markdown(f.read()))
		except:
			return "EXCEPTION: Couldn’t render %s.mdown." % page
			
	# render the page
	return "Wiki page: %s" % page
	
	
# if running brainerd directly, boot the app
if __name__ == "__main__":
	if not os.path.exists(root_dir) and not os.path.isdir(root_dir):
		print "Error: Root directory %s doesn't exist." % root_dir
		exit()
	app.run()
	