#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Description:  Removes ALL collections from ALL movies.
# Author:       /u/SwiftPanda16
# Requires:     plexapi, requests

from plexapi.server import PlexServer
import requests

### EDIT SETTINGS ###

PLEX_URL = "http://localhost:32400"
PLEX_TOKEN = "xxxxxxxxxx"
MOVIE_LIBRARY_NAME = "Movies"


## CODE BELOW ##

plex = PlexServer(PLEX_URL, PLEX_TOKEN)

headers = {"X-Plex-Token": PLEX_TOKEN}

for movie in plex.library.section(MOVIE_LIBRARY_NAME).all():
    if movie.collections:
        uri = '/library/sections/{}/all'.format(movie.librarySectionID)
        params = {'type': 1,
                  'id': movie.ratingKey,
                  'collection[].tag.tag-': ','.join(movie.collections),
                  'collection.locked': 0
                  }
        requests.put(PLEX_URL + uri, headers=headers, params=params)