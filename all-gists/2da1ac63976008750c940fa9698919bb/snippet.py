'''This script can be used to export data from Pocket (getpocket.com)
Uses include migrating to a different "read it later" service, saving
specific articles to another service, backing up your reading history,
and more.

Currently it can be used to export links and metadata for archived
articles with a given tag, which are more recent than a given timestamp.

An example use case is to export all articles you have tagged as
"to-export", which are newer than 10 days old. The timestamp functionality
allows you to run exports in a scheduled fashion without fetching
duplicate data.

The export result format is a large json blob, which can be further
processed as desired.

The script provides helper functions to:
- extract urls from the result
- backup the result to a file
- open the exported urls in a browser
'''

import requests
import json
import webbrowser
import argparse
import sys
import datetime
import time


base_url = "https://getpocket.com/v3/"
request_auth_url = "{}{}".format(base_url, "oauth/request")
complete_auth_url = "{}{}".format(base_url, "oauth/authorize")
get_url = "{}{}".format(base_url, "get")

def get_access_token(consumer_key):
    redirect_url = "test"
    auth_payload = {"consumer_key": consumer_key, "redirect_uri": redirect_url}

    r = requests.post(request_auth_url, json = auth_payload)
    request_token = r.text.split("=")[1]
    authorization_url = "https://getpocket.com/auth/authorize?request_token={}&redirect_uri={}".format(request_token, redirect_url)
    print("To get an access token, please go here: {}".format(authorization_url))

    r2 = requests.post(complete_auth_url, json = {"consumer_key": consumer_key, "code": request_token})
    access_token = "".join(r2.text.split("=")[1:]).split("&")[0]
    return access_token

def get_archive(consumer_key, access_token, tag, since):
    get_archive_payload = {
        "consumer_key": consumer_key,
        "access_token": access_token,
        "state": "archive",
        "tag": tag,
        "since": since
    }

    r = requests.post(get_url, json = get_archive_payload)
    return r.json()

def backup_data(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)

def extract_urls(data):
    return [v['resolved_url'] for v in data['list'].values()]

def open_urls(urls):
    for url in urls:
        webbrowser.open_new_tab(url)

def arg_to_timestamp(arg):
    return time.mktime(datetime.datetime.strptime(arg, "%Y-%m-%d").timetuple())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pocket Exporter Utility")
    parser.add_argument("--consumer_key", required=True, help="pocket platform app consumer key")
    parser.add_argument("--access_token", default="", help="user access token")
    parser.add_argument("--tag", required=True, help="article tag to export")
    parser.add_argument("--output", type=argparse.FileType('w'), default=sys.stdout, help="output location to store the export")
    parser.add_argument("--since", type=arg_to_timestamp, help="oldest date to pull archives from (YYYY-MM-DD)")

    args = parser.parse_args()
    token = args.access_token if args.access_token else get_access_token(args.consumer_key)
    archive = get_archive(args.consumer_key, token, args.tag, args.since)
    json.dump(archive, args.output, sort_keys=True, indent=2)
