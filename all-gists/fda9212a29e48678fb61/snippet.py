#!/usr/bin/python

import requests
import json
import re
import sys
import time
import os
import subprocess

username = 'jkominek'
testing = True
testing = False

def dumplastseen():
    with open("lastseen.json", "w") as f:
        json.dump(lastseen, f)

def parselink(link):
    parts = re.split("\s*,\s*", link)
    links = { }
    for part in parts:
        m = re.match("<(.+?)>; rel=\"(.+?)\"", part)
        links[m.group(2)] = m.group(1)
    return links

lastseen = json.load(open("lastseen.json"))

if testing:
    stars = json.load(open("cached.json"))
else:
    r = requests.get('https://api.github.com/users/%s/starred' % (username,),
                     headers={'User-Agent': username})
    stars = r.json()

    links = parselink(r.headers['link'])

    while links.has_key('next'):
        r = requests.get(links['next'],
                         headers={'User-Agent': username})
        stars += r.json()
        links = parselink(r.headers['link'])
        time.sleep(1.5)

    json.dump(stars, open("cached.json","w"))

to_update = [ ]
for star in stars:
    fullname = star['full_name']
    if (not lastseen.has_key(fullname)) or \
       star['pushed_at'] != lastseen[fullname]:
        to_update.append(star)

updated = 0
for i, star in zip(range(0, 1000), to_update):
    if i>0:
        time.sleep(60)

    fullname = star['full_name']
    print fullname, star['pushed_at']
    updated += 1
    user, proj = fullname.split('/')
    if not os.access(user, os.R_OK):
        os.mkdir(user)
    if os.access(fullname, os.R_OK):
        os.chdir(fullname)
        cmd = ["git", "fetch", "-p", "--all"]
        subprocess.check_call(cmd)
        os.chdir("../..")
    else:
        cmd = ["git", "clone", "--mirror", star['git_url'], fullname]
        subprocess.check_call(cmd)
    lastseen[fullname] = star['pushed_at']
    dumplastseen()

if updated>0:
    print "updated:", updated
