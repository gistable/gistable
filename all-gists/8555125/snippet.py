#!/usr/bin/env python

from gmusicapi import Musicmanager
from gmusicapi import Mobileclient

import sys
import os.path

params = sys.argv
if len(params) < 2:
    print "usage:" + sys.argv[0] + " filename [playlist name]"
    sys.exit()

file = params[1]

if len(params) == 3:
    plname = params[2]
else:
    plname = None

mm = Musicmanager()
api = Mobileclient()
mm.login()
api.login('GoogleID', 'Password')

track = mm.upload(file)
track_id = track[0][file]

if plname:
    playlist_id = None
    playlists = api.get_all_playlists()
    for playlist in playlists:
        if plname == playlist['name']:
            playlist_id = playlist['id']
            break

    if playlist_id == None:
        playlist_id = api.create_playlist(plname)

    api.add_songs_to_playlist(playlist_id, track_id)
