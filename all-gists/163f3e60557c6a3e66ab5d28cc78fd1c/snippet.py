'''
kill_transcode function from https://gist.github.com/Hellowlol/ee47b6534410b1880e19

PlexPy > Settings > Notification Agents > Scripts > Bell icon:
        [X] Notify on pause
        
PlexPy > Settings > Notification Agents > Scripts > Gear icon:
        Playback Pause: kill_trans_pause.py

'''

import requests
import sys
import json
import platform
from uuid import getnode


## EDIT THESE SETTINGS ##

PLEX_HOST = ''
PLEX_PORT = 32400
PLEX_SSL = '' # s or ''
PLEX_TOKEN = '<token>'
PLEXPY_APIKEY = 'XXXXXX'  # Your PlexPy API key
PLEXPY_URL = 'http://localhost:8181/'  # Your PlexPy URL

ignore_lst = [] # ['username1', 'username2']

class Activity(object):
    def __init__(self, data=None):
        d = data or {}
        self.rating_key = d['rating_key']
        self.title = d['full_title']
        self.user = d['user']
        self.user_id = d['user_id']
        self.video_decision = d['video_decision']
        self.transcode_decision = d['transcode_decision']
        self.transcode_key = d['transcode_key']
        self.state = d['state']


def get_get_activity():
    # Get the current activity on the PMS.
    payload = {'apikey': PLEXPY_APIKEY,
               'cmd': 'get_activity'}

    try:
        r = requests.get(PLEXPY_URL.rstrip('/') + '/api/v2', params=payload)
        response = r.json()
        res_data = response['response']['data']['sessions']
        return [Activity(data=d) for d in res_data]

    except Exception as e:
        sys.stderr.write("PlexPy API 'get_activity' request failed: {0}.".format(e))


def fetch(path, t='GET'):
    url = 'http%s://%s:%s/' % (PLEX_SSL, PLEX_HOST, PLEX_PORT)

    headers = {'X-Plex-Token': PLEX_TOKEN,
               'Accept': 'application/json',
               'X-Plex-Provides': 'controller',
               'X-Plex-Platform': platform.uname()[0],
               'X-Plex-Platform-Version': platform.uname()[2],
               'X-Plex-Product': 'Plexpy script',
               'X-Plex-Version': '0.9.5',
               'X-Plex-Device': platform.platform(),
               'X-Plex-Client-Identifier': str(hex(getnode()))
               }

    try:
        if t == 'GET':
            r = requests.get(url + path, headers=headers, verify=False)
        elif t == 'POST':
            r = requests.post(url + path, headers=headers, verify=False)
        elif t == 'DELETE':
            r = requests.delete(url + path, headers=headers, verify=False)

        if r and len(r.content):  # incase it dont return anything
            return r.json()
        else:
            return r.content

    except Exception as e:
        print e


def kill_transcode(transcode_key):
    print fetch('video/:/transcode/universal/stop?session=' + transcode_key)

activity = get_get_activity()

for a in activity:
    if a.state == 'paused' and a.transcode_decision == 'transcode' and a.user not in ignore_lst and a.transcode_key:
        sys.stdout.write("Killing {a.user}'s transcode stream of {a.title}".format(a=a))
        kill_transcode(a.transcode_key)