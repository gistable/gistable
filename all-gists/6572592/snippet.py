#!/usr/bin/env python

# Lastfm loved tracks to Google Music All Access playlist. As noted in the comments you do need the All Access subscription thing otherwise it will always find 0 songs.
#
# Written by Tim Hutt, tdhutt@gmail.com, based on this script:
#
# https://gist.github.com/oquno/3664731
#
# Today is the 15th of September 2013.
#
# Not really tested!
#
# Update on 20th of September 2016:
#
#  * Changed login API to match gmusicapi (not tested at all)
#
# Instructions:
#
# 0. Install python and pip.
# 1. Download this to a file `lastfm_to_gmusic.py`
# 2. Make it executable: `chmod +x lastfm_to_gmusic.py`
# 3. Install `gmusicapi` using `pip`: `pip install gmusicapi`
# 4. Get a last.fm API key here: http://www.last.fm/api/account/create
# 5. Run it! `./lastfm_to_gmusic.py`.
#
# Troubleshooting:
#
# 1. It says "Login error": Go to your gmail and check that it didn't block any "suspicious logins".
# 2. It doesn't find any tracks: Update gmusicapi.
# 3. Something else: Email me. There's a small chance I'll reply.
#
#


import urllib, urllib2
import gmusicapi
from xml.etree.ElementTree import *

def main():
    # Gather required info.
    google_username = raw_input("Google username: ").strip()
    google_password = raw_input("Google password: ")
    lastfm_username = raw_input("Lastfm username: ").strip()
    lastfm_key = raw_input("Lastfm API key: ").strip()

    # Log in.
    api = gmusicapi.Mobileclient()
    if not api.login(google_username, google_password, gmusicapi.Mobileclient.FROM_MAC_ADDRESS):
        print "Login error"
        return

    # Get loved tracks.
    loved = []
    page = 1
    while True:
        url = "http://ws.audioscrobbler.com/2.0/?method=user.getlovedtracks&user=%s&api_key=%s&page=%d" % \
              (lastfm_username, lastfm_key, page)
        print("Fetching: " + url)
        tree = parse(urllib2.urlopen(url)).getroot()
        tracks = tree.findall('lovedtracks/track')
        for track in tracks:
            title = track.find('name').text
            artist = track.find('artist/name').text
            loved.append((artist,title))
        if len(tracks) < 50:
            break
        page += 1

    print("Got " + str(len(loved)) + " loved tracks")

    if len(loved) == 0:
        print "Exiting"
        return

    # Creating new playlist
    playlist_id = api.create_playlist("Loved tracks")

    to_add = []
    # Search for each song in all access.

    # This is quite a dirty way to do it, and the gmusicapi seems to be a little out of date
    # hence the catch-all. This found 529 out of the 787 loved songs I have which is not too bad.
    for target in loved:
        try:
            res = api.search_all_access(target[0] + " " + target[1], max_results=1)
            to_add.append(res["song_hits"][0]["track"]["nid"])
        except:
            pass
        print("Got " + str(len(to_add)) + " songs so far out of " + str(len(loved)))

    print("Adding " + str(len(to_add)) + " songs to playlist")

    api.add_songs_to_playlist(playlist_id, to_add)

    print("Done! I hope.")


if __name__ == '__main__':
    main()
