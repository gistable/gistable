#coding: utf-8
import keychain
import console
import editor
 
import time
import re
 
import requests
import json
import base64
 
SITE_BRANCH = 'gh-pages' # either main or gh-pages
COMMITTER = {'name': '$github_username', 'email': '$github_email'}
 
username = '$github_username'
token = '$github_token'
repo = '$github_repo'
 
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
		  
	if post_title:
		safe_title = re.sub('[^a-zA-Z0-9\s]', '', post_title).replace(' ', '-')
		safe_title.replace('--', '-')
		if not date:
			date = time.strftime('%Y-%m-%d', time.gmtime())
    
		post_filename = '_posts/%s-%s.markdown' % (date, safe_title)
		
		URL = 'https://api.github.com/repos/%s/%s/contents/%s' % (username, repo, post_filename)
		
		header = {
			'Authorization': 'token %s' % token,
			'User-Agent': username
		}
		
		get_data = {
			'path': post_filename,
			'ref': SITE_BRANCH
		}
 
		response = requests.get(URL, headers=header, params=get_data)
		response_json = response.json()
 
		if response.status_code == 404:     # File doesn't exist, create it.
			data = {
				'path': post_filename,
				'content': base64.b64encode(post_text),
				'message': 'Blog Post - %s' % post_title,
				'branch': SITE_BRANCH,
				'committer': COMMITTER
			}
 
			response = requests.put(URL, headers=header, data=json.dumps(data))
			
			if response.status_code == 201:
				console.hud_alert("Blog post created successfully.", 'success', 2)
			else:
				console.alert("Commit failed.")
		elif response.status_code == 200:   # File exists, update it.
			data = {
				'path': post_filename,
				'content': base64.b64encode(post_text),
				'message': 'Blog Post - %s' % post_title,
				'branch': SITE_BRANCH,
				'committer': COMMITTER,
				'sha': response_json['sha']
			}
 
			response = requests.put(URL, headers=header, data=json.dumps(data))
			
			if response.status_code == 200:
				console.hud_alert("Blog post updated successfully.", 'success', 2)
			else:
				console.alert("Commit failed.")
		else:                        # Something went wrong!
			console.alert("There was a problem with the server.")
 
	else:
		console.alert("Couldn't find a title.\n\nAction Halted.")
		
else:
	console.alert("No YAML header found.\n\nAction Halted.")
