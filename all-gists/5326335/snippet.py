#!/usr/bin/env python
#
# Find and replace tracker urls in a Deluge torrents.state
#
# Need to edit the variables: orig_tracker_url and new_tracker_url

import os
import sys
import platform
import shutil
import cPickle

orig_tracker_url = 'udp://xxx'
new_tracker_url = 'udp://xxx'

if platform.system() in ('Windows', 'Microsoft'):
    state_file_path = os.path.join(os.environ.get('APPDATA'), 'deluge', 'state', 'torrents.state')
    deluge_dir = os.path.join(os.environ['ProgramFiles'], 'Deluge')
    if os.path.isdir(deluge_dir):
        sys.path.append(deluge_dir)
        for item in os.listdir(deluge_dir):
            if item.endswith(('.egg', '.zip')):
                sys.path.append(os.path.join(deluge_dir, item))
else:
    state_file_path = os.path.expanduser('~/.config/deluge/state/torrents.state')

print("State file: %s" % state_file_path)
print("Replace '%s' with '%s'" % (orig_tracker_url, new_tracker_url))
state_file = open(state_file_path, 'rb')
state = cPickle.load(state_file)
state_file.close()

state_modified = False
for torrent in state.torrents:
    for tracker in torrent.trackers:
        if tracker['url'] == orig_tracker_url:
            tracker['url'] = new_tracker_url
            state_modified = True


if state_modified:
    shutil.copyfile(state_file_path, state_file_path + '.old')
    state_file = open(state_file_path, 'wb')
    cPickle.dump(state, state_file)
    state_file.close()
    print("State Updated")
else:
    print("Nothing to do")