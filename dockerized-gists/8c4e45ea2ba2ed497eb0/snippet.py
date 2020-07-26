#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Dirty script to check if any forks in ahead of main and open that branch commitlist
Warning: Uses alot of api calls
"""

import requests
from requests.auth import HTTPBasicAuth
import json
import webbrowser
from math import ceil
import time

### My username and password ###
username = ''
password = ''

### Open a the commitlist on github if repo is a head of branch/main ###
openbrwser = False

### Github user and repo to check ###
usr = "styxit"
rpo = "HTPC-Manager"

### Placeholders ###
branches_ahead = 0
apicalls = 0
apicalls_left = 0
ahead_list = []
apicalls_reset = None
start_time = None


def behind_by(fork, latest, branch):
    global usr
    global openbrwser
    global ahead_list
    global branches_ahead

    mrepo = "%s:main" % usr
    try:
        url = 'https://api.github.com/repos/%s/compare/%s:%s...%s' % (fork, usr, branch, branch)
        result = fetch(url)
        if result["message"] == "Not Found":
            url = 'https://api.github.com/repos/%s/compare/%s...%s' % (fork, mrepo, branch)
            result = fetch(url)

    except:
        pass

    try:
        if result["total_commits"] > 0 and result["ahead_by"] > 0:
            branches_ahead += 1
            curl = "https://github.com/%s/commits/%s" % (fork, branch)
            print "Ahead", result["total_commits"], fork, branch, curl

            d = {
                "fork": fork,
                "branch": branch,
                "ahead": result["ahead_by"],
                "url": curl
                }

            ahead_list.append(d)
            if openbrwser:
                webbrowser.open(curl, new=2, autoraise=False)
    except:
        pass

# Isnt used for anything
def latest_commit(fork, branch):
    url = 'https://api.github.com/repos/%s/commits/%s' % (fork, branch)
    lastest = fetch(url)
    behind_by(fork, lastest, branch)


def findbranches(fork):
    url = "https://api.github.com/repos/%s/branches" % fork
    branches = fetch(url)
    for branch in branches:
        behind_by(fork, lastest, branch)
        #latest_commit(fork, branch["name"])


def find_all_forks():
    """ Finds all forks, check if the result is more then 30, follow links"""
    global usr
    global rpo
    global apicalls
    global apicalls_left
    global ahead_list
    global apicalls_reset
    global start_time

    start_time = time.time()
    # Find all the repos of the user
    url = "https://api.github.com/users/%s/repos" % usr
    result = fetch(url)
    # Try to find the correct repo
    for r in result:
        # Found correct repo
        if r["name"] == rpo:
            #Round up

            pages = float(r["forks_count"])/ 30  # Results per page
            pages_round = ceil(pages)
            # make baseurl
            baseurl = "https://api.github.com/repositories/%s/forks?page=" % r["id"]
            for l in range(1, int(pages_round) + 1):
                forks = fetch("%s%s" % (baseurl, l))

                for fork in forks:
                    findbranches(fork["full_name"])
            
            print "\n"
            print "There was %s forks in total" % r["forks_count"]
            print "There was %s branches ahead" % branches_ahead
            print "%i apicalls left" % int(apicalls_left)
            print "Api limit will reset in %s" % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(apicalls_reset)))
            print '"Scan" took %s sec' % (time.time() - start_time)
            print ahead_list
            


def fetch(url):
    ''' Used to connect to github api'''
    global username
    global password
    global apicalls
    global apicalls_left
    global apicalls_reset
    try:
        #Github api req user-agent
        headers = {'User-Agent': 'Mozilla/5.0'}
        data = requests.get(url, auth=HTTPBasicAuth(username, password), timeout=15, headers=headers)
        apicalls += 1
        apicalls_left = data.headers["X-RateLimit-Remaining"]
        apicalls_reset = data.headers["X-RateLimit-Reset"]

        #print "%s sec" % (time.time() - start_time)
        # data.json() returns a error
        return json.loads(data.text)
    except Exception as e:
        print e, url


find_all_forks()
