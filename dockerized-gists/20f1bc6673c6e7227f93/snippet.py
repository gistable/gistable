#!/usr/bin/env python

""" WARNING: crypto is hard to do right, bugs are hard to discover. Don't use if you life depends on it. """

import os.path
from subprocess import Popen, PIPE
import json

# requests and beautifulsoup should be in your favorite package manager already
import requests
import bs4

# this is the configuration from the keybase nodejs client, needed to extract the 
# keybase user id, which is needed for APICALL below
CONFIG = "~/.config/keybase/config.json"

# this is undocumented, but used on the keybase website to "show more" tracked than already loaded
APICALL = "https://keybase.io/_/api/1.0/user/load_more_followers.json?reverse=1&uid=%s&last_uid=%s"

keybase_config = json.load(file(os.path.expanduser(CONFIG)))["user"]

print "Found keybase user", keybase_config["name"]

uid = keybase_config["id"]

r = requests.get(APICALL % (uid, uid)).json()

# yes, the data is html inside json
soup = bs4.BeautifulSoup(r["snippet"])

for user in soup.find_all(class_="follower-row"):
    user_id = user.find(class_="td-follower-info").find("a")["href"][1:]
    
    print "Fetching key for", user_id
    key = requests.get("https://keybase.io/%s/key.asc" % user_id).text
    
    print "Importing key for", user_id
    gpg = Popen('gpg --import', stdin=PIPE, shell=True)
    gpg.stdin.write(key)
    gpg.stdin.close()
    gpg.wait()