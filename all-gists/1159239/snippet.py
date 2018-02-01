#!/usr/bin/env python
# Script to clone all the github repos that a user is watching
import requests
import json
import subprocess

# Grab all the URLs of the watched repo
user = 'jharjono'
r = requests.get("http://github.com/api/v2/json/repos/watched/%s" % (user))
repos = json.loads(r.content)
urls = [repo['url'] for repo in repos['repositories']]

# Clone them all
for url in urls:
	cmd = 'git clone ' + url
	pipe = subprocess.Popen(cmd, shell=True)
	pipe.wait()

print "Finished cloning %d watched repos!" % (len(urls))
