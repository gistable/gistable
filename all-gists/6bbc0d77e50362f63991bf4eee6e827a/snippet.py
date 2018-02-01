#!/usr/bin/env python3

import csv
import datetime
import getpass
import os
import re
import sys
import time

import requests


def request(*args, **kwargs):
    retry = True
    while retry:
        try:
            response = requests.post(*args, **kwargs)
            response.raise_for_status()
            retry = False
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                time.sleep(int(e.response.headers['Retry-After']))
                retry = True
            elif e.response.status_code >= 500:
                time.sleep(0.5)
                retry = True
            else:
                raise

    return response.json()


__user_cache = {}


def get_user_name(api_token, user_id):
    if user_id not in __user_cache:
        response_data = request(
            'https://slack.com/api/users.info',
            data={
                "token": api_token,
                "user": user_id,
            }
        )
        if not response_data['ok']:
            __user_cache[user_id] = user_id
        else:
            __user_cache[user_id] = response_data['user'].get('real_name') or response_data['user'].get('name') or "Unknown"
    return __user_cache[user_id]


__channel_cache = {}


def get_channel_name(api_token, channel_id):
    if channel_id not in __channel_cache:
        response_data = request(
            'https://slack.com/api/conversations.info',
            data={
                "token": api_token,
                "channel": channel_id,
            }
        )
        if not response_data['ok']:
            __channel_cache[channel_id] = channel_id
        else:
            __channel_cache[channel_id] = response_data['channel'].get('name')
    return __channel_cache[channel_id]


def decode_message(api_token, message):
    # channels
    message = re.sub(
        r"<#([^|>]+)(?:\|([^>]+))?>",
        lambda match: "#{}".format(match.group(2) if match.group(2) else get_channel_name(api_token, match.group(1))),
        message
    )
    # users
    message = re.sub(
        r"<@([^|>]+)(?:\|([^>]+))?>",
        lambda match: match.group(2) if match.group(2) else get_user_name(api_token, match.group(1)),
        message
    )
    # URLs
    message = re.sub(
        r"<([^|>]+)(?:\|([^>]+))?>",
        lambda match: "{} ({})".format(*match.groups()[1:3]) if len(match.groups()) > 2 else match.group(1),
        message
    )
    message = message.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
    return message


def get_messages(api_token, channel_id, from_=0, to=None):
    cursor = None
    while True:
        data = {
            "token": api_token,
            "channel": channel_id,
            "inclusive": "true",
            "limit": 200,
        }
        if cursor:
            data['cursor'] = cursor
        if from_:
            data['oldest'] = str(from_)
        if to:
            data['latest'] = str(to)
        response_data = request(
            'https://slack.com/api/conversations.history',
            data=data
        )
        if not response_data['ok']:
            raise RuntimeError(response_data['error'])
        yield from response_data['messages']
        cursor = response_data.get('response_metadata', {}).get('next_cursor')
        if cursor is None:
            break


def main(api_token, channel_id, from_=0, to=None):
    writer = csv.writer(sys.stdout)
    writer.writerow(['Time', 'User', 'Message'])
    for message in get_messages(api_token, channel_id, from_, to):
        if message['type'] != 'message':
            continue
        writer.writerow([
             datetime.datetime.fromtimestamp(int(message['ts'].split('.',1)[0])).strftime('%Y-%m-%d %H:%M:%S'),
             get_user_name(api_token, message.get('user')) if message.get('user') else "Unknown",
             decode_message(api_token, message['text'])
        ])


if __name__ == "__main__":
    api_token = os.getenv('SLACK_API_TOKEN')
    while not api_token:
        api_token = getpass.getpass('Enter your API token: ')
    channel_id = sys.argv[1]
    main(api_token, channel_id)
