#coding: utf-8
import keychain
import console
import editor

import time
import re

import requests
import json
import base64

SITE_BRANCH = 'gh-pages' # either master or gh-pages

#keychain.delete_password('GitHub', 'username')
#keychain.delete_password('GitHub', 'token')
#keychain.delete_password('GitHub', 'repository')

# Get Username, API Token and Repository
username = keychain.get_password('GitHub', 'username')
if not username:
	username = console.input_alert("Username", "Enter your GitHub Username", '', "Save")
	keychain.set_password('GitHub', 'username', username)
	
tokn = keychain.get_password('GitHub', 'token')
if not tokn:
	tokn = console.password_alert("API Token", "Enter your GitHub API Token", '', "Save")
	keychain.set_password('GitHub', 'token', tokn)

repo = keychain.get_password('GitHub', 'repository')
if not repo:
	repo = console.input_alert("Repository", "Enter your GitHub Repository name", '', "Save")
	keychain.set_password('GitHub', 'repository', repo)

# Mangle the post ;)
post_text = editor.get_text()

post_sections = post_text.split('---')
if len(post_sections) > 1:
	yaml_header = post_sections[1].splitlines()
	
  # Find the title in the YAML
	post_title = None
	date = None
	for line in yaml_header:
		if line[:6] == 'title:':
			post_title = line[6:].strip()
		elif line[:5] == 'date:':
			date = line[5:].strip()[:10]
	
	if post_title and date:
		safe_title = re.sub('[^a-zA-Z0-9\s]', '', post_title).replace(' ', '-')
		safe_title.replace('--', '-')
    
		post_filename = '_posts/%s-%s.markdown' % (date, safe_title)
		
		URL = 'https://api.github.com/repos/%s/%s/contents/%s' % (username, repo, post_filename)
		
		header = {
			'Authorization': 'token %s' % tokn,
			'User-Agent': username
		}
		
		get_data = {
			'path': post_filename,
			'ref': SITE_BRANCH
		}

		response = requests.get(URL, headers=header, params=get_data)
		response_json = response.json()

		if response.status_code == 200:
			new_text = base64.b64decode(response_json['content'])
			editor.replace_text(0, len(post_text), new_text)
			console.hud_alert("Post downloaded from GitHub.", 'success', 2.0)
		else:                        # Something went wrong!
			console.alert("This post does not exist.")

	else:
		console.alert("Couldn't find a title or date.\n\nAction Halted.")
		
else:
	console.alert("No YAML header found.\n\nAction Halted.")