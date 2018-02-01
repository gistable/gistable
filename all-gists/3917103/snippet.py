import os
from subprocess import call
from gmusicapi import api

g = api.Api()
print "Loging..."
g.login("email", "password")
print "OK !"

for song in g.get_all_songs():
    if not song["artist"]:
        song["artist"] = "Undefined"
    path = os.path.join("Musique", song["artist"])
    if not os.path.exists(path):
        call(["mkdir", path])
    if not song["album"]:
        song["album"] = "Undefined"
    if song["year"]:
        path = os.path.join(path, str(song["year"]) + " - " + song["album"])
    else:
        path = os.path.join(path, song["album"])
    if not os.path.exists(path):
        call(["mkdir", path])
    if song["track"]:
        if song["track"] < 10:
            song["track"] = "0" + str(song["track"])
        else:
            song["track"] = str(song["track"])
        path = os.path.join(path, song["track"] + " - " + song["title"] + ".mp3")
    else:
        path = os.path.join(path, song["title"] + ".mp3")
    print "PATH :", path
    if not os.path.exists(path):
        link, nb = g.get_song_download_info(song["id"])
        print "Downloading", link, "-", nb
        call(["wget", link, "-O", path])
    print "---"
