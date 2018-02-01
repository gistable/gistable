#!/usr/bin/python
import json
import ssl
import time
from urllib2 import Request, urlopen, URLError

url = "https://172.16.1.149:1337/api"
token = "fvcds7..."
live_agents = []

def get_agents():
    url = url + '/agents?token='+token
    request = Request(url)

    try:
        empire_agents = json.load(urlopen(request, context=ssl._create_unverified_context()))
        for agent in empire_agents['agents']:
            if agent['name'] not in live_agents:
                live_agents.append(agent['name'])
                message = "Agent "+ agent['name'] + " on "+ agent['hostname'] + " has just checked in"
                post_message(message)

    except URLError, e:
        print "nope", e

def post_message(agent_info):
    slack_url = 'https://hooks.slack.com/services/[your_own_token_here]'
    data = '{"channel": "@bneg", "username": "Emperor Palpatine", "text": "'+ agent_info +'"}'
    urlopen(slack_url, data)


def main():

    while True:
        get_agents()
        time.sleep(5)


if __name__ == "__main__":
    main()