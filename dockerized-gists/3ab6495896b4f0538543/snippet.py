#!/usr/bin/env python
# coding=utf-8

import os
import sys
import requests
import time

def get_track_json(track_id):
    url = 'https://api.spotify.com/v1/tracks/' + track_id
    req = requests.get(url)
    time.sleep(0.5)
    if req.status_code == 200:
        return req.json()
    else:
        print("URL returned non-200 HTTP code: " +
              str(req.status_code))
    return None

def main():
    if len(sys.argv) != 2:
        print("USAGE: " + sys.argv[0] + " file_name")
        sys.exit(1)

    file_name = sys.argv[1]
    if not os.path.exists(file_name):
        print(file_name + " does not exist")
        sys.exit(1)

    with open(file_name, 'r') as f:
        failures = [uri.strip() for uri in f.readlines()]
        for uri in failures:
            uri_tokens = uri.split(':')
            if len(uri_tokens) != 3:
                print("Invalid URI: " + uri)
                continue

            track_json = get_track_json(uri_tokens[2])
            if track_json is None:
                print("Did not receive json back, skipping...")
                continue

            print(track_json["artists"][0]["name"] + " - " +
                  track_json["name"])


if __name__ == '__main__':
    main()
