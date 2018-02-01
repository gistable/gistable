#!/usr/bin/python

from mpd import MPDClient
from random import randint, shuffle

client = MPDClient()
client.connect('localhost', 6600)

albums = client.list("album")
shuffle(albums)

randAlbum = albums[randint(0, len(albums)-1)]
artists = client.list("artist", "album", randAlbum)
if len(artists) > 1:
	artist = artists[randint(0, len(artists)-1)]
else:
	artist = artists[0]

files = client.list("filename", "album", randAlbum)
client.clear()

for file in files:
	client.add(file)
client.play()
print("Playing \"%s - %s\"" % (artist, randAlbum))

client.close()
client.disconnect()

