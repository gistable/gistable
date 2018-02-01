
"""
This is a simple script showing how you can used plexpys notifications system to kill a stream

Possible plexpyargs: -tk {transcode_key} -u {username} -td {transcode_decision} -t 20:20 -ln Secret_tash

Instructions:

    1. Save the script somewhere on your computer as kill_a_stream.py.

    2. Edit the variables at the top of the script:
        The host, port, token, and ssl, can be the same as in the PlexPy settings
        Edit the list of blocked_users, separated by a comma.

    3. PlexPy > Settings > Notification Agents > Scripts > Bell icon:
        [X] Notify on playback start
        [X] Notify on playback resume

    4. PlexPy > Settings > Notification Agents > Scripts > Gear icon:
        Enter the "Script folder" where you save the script from step 1.
        Playback Start: kill_a_stream.py
        Playback Resume: kill_a_stream.py
        Save

    5. PlexPy > Settings > Notifications > Script > Script Arguments:
        -tk {transcode_key} -u {username} -td {transcode_decision}

    Any time one of the blocked_users starts a transcoded session, the script will stop the stream.

    You can also supply a -t 20:30 and the script will only kill a stream after 20:30 or disallow transcode from a library with -ln

"""


import argparse
import requests
from uuid import getnode
import platform
from datetime import datetime


### Edit me ###
host = '10.0.0.97'
port = 32400
token = '<token>'
ssl = '' # s or ''
kill_time = ''  # time for date in 20:00 format
blocked_users = 'Hellowlol'  # 'username1, username2'
blocked_librarys = '' # 'PG-18, adult'
### stop ###


def tcomp(kill_time):
    zz = False
    if kill_time:
        tk = kill_time.split(':')
        h = int(tk[0])
        m = int(tk[1])
        zz = datetime(2009, 12, 2, h, m).time()
    return zz

def fetch(path, t='GET'):
    url = 'http%s://%s:%s/' % (ssl, host, port)

    headers = {'X-Plex-Token': token,
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


def now():
    return datetime.now().time()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-tk', '--transcode_key', action='store', default='',
                        help='Transcode key of the the current stream to kill')

    parser.add_argument('-u', '--user', action='store', default=None,
                        help='username of the person watching a stream')

    parser.add_argument('-td', '--transcode_decision', action='store', default=None,
                        help='transcode decision')

    parser.add_argument('-ln', '--library_name', action='store', default=blocked_librarys,
                        help='What library was this played from')

    parser.add_argument('-t', '--time', action='store', default=kill_time,
                        help='Kill only streams if clock is above t')

    p = parser.parse_args()

    if p.user in [bu.strip() for bu in blocked_users.split(',')] and p.transcode_decision.lower() == 'transcode' and not p.time:
        kill_transcode(p.transcode_key)

    # You can also kill any transcodes based on time by passing the -t parameter or editing the kill_tme
    elif p.time and now() > tcomp(p.time) and p.transcode_decision.lower() == 'transcode' and p.user in [bu.strip() for bu in blocked_users.split(',')]:
        kill_transcode(p.transcode_key)

    elif p.library_name in [bln.strip() for bln in blocked_librarys.split(',')] and p.user in [bu.strip() for bu in blocked_users.split(',')] and p.transcode_decision.lower() == 'transcode':
        kill_transcode(p.transcode_key)
