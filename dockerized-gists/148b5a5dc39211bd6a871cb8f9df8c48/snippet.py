#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Description:  Create a Plex collection from a text file list of rating keys.
# Author:       /u/SwiftPanda16
# Requires:     plexapi, requests


import requests
from plexapi.server import PlexServer


### EDIT SETTINGS ###

PLEX_URL = 'http://localhost:32400'
PLEX_TOKEN = 'xxxxxxxxxx'
PLEX_LIBRARY_NAME = 'Movies'
COLLECTION_NAME = 'New Collection'
TEXT_FILE_LIST = '/path/to/rating_keys.txt'  # One rating key (media ID) per line


### CODE BELOW ###

def add_collection(media_item):
    library_key = media_item.librarySectionID
    rating_key = media_item.ratingKey
    collection_key = "collection[{key}].tag.tag".format(key=len(media_item.collections))

    headers = {"X-Plex-Token": PLEX_TOKEN}
    params = {"type": 1,
              "id": rating_key,
              "collection.locked": 1,
              collection_key: COLLECTION_NAME
              }

    url = "{base_url}/library/sections/{library}/all".format(base_url=PLEX_URL, library=library_key)
    r = requests.put(url, headers=headers, params=params)

    
def main():
    try:
        plex = PlexServer(PLEX_URL, PLEX_TOKEN)
    except:
        print("No Plex server found at '{base_url}', or invalid token.".format(base_url=PLEX_URL))
        print("Exiting script.")
        return

    rating_keys = []
    with open(TEXT_FILE_LIST, 'r') as f:
        for line in f:
            rating_keys.append(line.rstrip())

    for key in rating_keys:
        try:
            media_item = plex.library.getByKey(key)
            if COLLECTION_NAME.lower() not in [c.tag.lower() for c in media_item.collections]:
                add_collection(media_item)
            else:
                print("Collection '{collection}' already exists for rating key '{key}'. Skipping.".format(key=key, collection=COLLECTION_NAME))
                continue
        except:
            print("Rating key '{key}' not found in library '{library}'. Skipping.".format(key=key, library=PLEX_LIBRARY_NAME))
            pass


if __name__ == "__main__":
    main()