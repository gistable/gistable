#!/usr/local/bin/python3

import requests
import json

# User Configuration
PB_USERNAME = "your Pinboard username"
PB_PASSWORD = "your Pinboard password"
PB_PATH = "/absolute/path/to/file/PinboardUnread.json"
# End Configuration

PB_URL = "https://api.pinboard.in/v1/posts/all?format=json"

r = requests.get(PB_URL, auth=((PB_USERNAME, PB_PASSWORD)))
data = json.loads(r.text)
toread = [{"title": i["description"], "subtitle": i["extended"], "url": i["href"], "actionArgument": {"shared": i["shared"], "tags": i["tags"]}, "action": "markAsRead.py", "actionRunsInBackground": bool("true")} for i in data if i["toread"] == "yes"]

with open(PB_PATH, "w+") as the_file:
	print(json.dumps(toread), file=the_file)