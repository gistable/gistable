#!/usr/bin/env python

############################### README ###############################
# External dependencies:
# * libmagic
# * python-dateutil
# * python-magic
# * requests
#
# The shell command call at the end was tested with GNU date from GNU
# coreutils. Other implementations might not work (for instance, BSD
# date is not compatible). However, you may comment out the last
# section without affecting the download.
#
# The "last_update_timestamp" is reserved for the update feature,
# which is not implemented yet.
######################################################################

import commands
import json
import os
import sys
import urllib

import dateutil.parser
import magic
import requests

########################### CUSTOMIZE THIS ###########################
page_id = "567045406742962"
access_token = "app_id|app_secret" # see https://developers.facebook.com/docs/facebook-login/access-tokens#apptokens
dest = os.path.expanduser("~/img/sns/apink-official-facebook")
website_title = "apink-official-facebook"
######################################################################

if not os.path.exists(dest):
    os.makedirs(dest)

# read last update time, if it is available
last_update_record = dest + "/last_update_timestamp"
if os.path.exists(last_update_record):
    f = open(last_update_record, "r")
    last_update_timestamp = f.readline()
    f.close()
    last_update_time = dateutil.parser.parse(last_update_timestamp)
else:
    last_update_time = dateutil.parser.parse("1970-01-01T00:00+00:00")

# this function makes an API call with only an access_token (which
# could be just app-id|app-secret)
def fb_public_call(endpoint, params, access_token):
    params["access_token"] = access_token
    response = requests.get("https://graph.facebook.com/" + endpoint,
                            params=params)
    return response.json()

# this function downloads a photo
# return codes are defined below
SUCCESS = 0
FAILED_DOWNLOAD = 1
UNRECOGNIZED_MIME = 2
OLD_PHOTO = 255 # photo older than last update time
def handle_photo(photo, album_id):
    # print information
    photo_id = photo["id"]
    time = dateutil.parser.parse(photo["created_time"])
    if time < last_update_time:
        return OLD_PHOTO
    time_print = time.strftime("%b %d, %Y")
    time_full = time.strftime("%Y%m%d%H%M%S")
    original_image = photo["images"][0]
    height = original_image["height"]
    width = original_image["width"]
    format_string = "date: %s   id: %s   size: %sx%s"
    print format_string % (time_print, photo_id, width,
                           height)
    # download file
    source_uri = original_image["source"]
    filename = time_full + "-" + website_title + "-" + \
               album_id + "-" + photo_id
    filepath = dest + "/" + filename
    urllib.urlretrieve(source_uri, filepath)
    # identify mime type and attach extension
    if os.path.exists(filepath):
        mime = magic.from_file(filepath, mime=True)
        if mime == "image/gif":
            newfilepath = filepath + ".gif"
        elif mime == "image/jpeg":
            newfilepath = filepath + ".jpg"
        elif mime == "image/png":
            newfilepath = filepath + ".png"
        else:
            err = filepath + ": error: " + \
                  "unrecgonized image type\n"
            sys.stderr.write(err)
            return UNRECOGNIZED_MIME
        os.rename(filepath, newfilepath)
        return SUCCESS
    else:
        # donwload failed for whatever reason
        err = "error: " + filename + " failed to " + \
              "downloaded from " + source_uri + "\n"
        sys.stderr.write(err)
        return FAILED_DOWNLOAD

# this function handles an album, i.e., download newly added photos
# since the last update
def handle_album(album):
    # print album info
    album_id = album["id"]
    format_string = "downloading album \"%s\" " + \
                    "(album id: %s; photo count: %s)"
    print format_string % (album["name"], album_id,
                           album["count"])
    print "-" * 80
    # retrieve photos in the album
    photos_response = fb_public_call(album["id"] + "/photos",
                                     params, access_token)
    while True:
        for photo in photos_response["data"]:
            if handle_photo(photo, album_id) == OLD_PHOTO:
                # already encountered old photo in this album
                # no need to look further into the past
                print
                return

        if "next" in photos_response["paging"]:
            next_uri = photos_response["paging"]["next"]
            photos_response = requests.get(next_uri).json()
        else:
            break
    print
    
params = {}
# retrieve albums
albums_response = fb_public_call(page_id + "/albums", params,
                                 access_token);
while True:
    for album in albums_response["data"]:
        handle_album(album)

    if "next" in albums_response["paging"]:
        next_uri = albums_response["paging"]["next"]
        albums_response = requests.get(next_uri).json()
    else:
        break

# update feature yet to be implemented
# create a file "last_update_timestamp" for future use
f = open(last_update_record, "w")
f.write(commands.getoutput("date -u --iso-8601=seconds"))
f.close()
