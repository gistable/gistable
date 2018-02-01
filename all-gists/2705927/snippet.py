#!/usr/bin/python

###############################################################################
# Produce a collage (grid) of friend profile images from Facebook.
# Inspired by Vipin "swvist" Nair @ https://gist.github.com/2692786
###############################################################################
# Copyright (c) 2012 Madzen
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
###############################################################################

from urllib import urlopen
import json
from PIL import Image
from random import choice
import cStringIO
from argparse import ArgumentParser
from hashlib import md5

###########################
# User Configuration
###########################

# Access token from Facebook (need to acquire and add here or command-line)
access_token = '<ADD_ACCESS_TOKEN>'

###########################
# End of User Configuration
###########################

parser = ArgumentParser(description='Creates a grid of Facebook profile pictures.')

parser.add_argument('-c', '--colour', help='produce a colour image',
                    action='store_true')
parser.add_argument('-o', '--output', dest='outfile',
                    help='output filename (default: output.jpg)')
parser.add_argument('-w', '--width', type=int, dest='width',
                    help='number of images wide (default: 30)')
parser.add_argument('-l', '--height', type=int, dest='height',
                    help='number of images high (default: 25)')
parser.add_argument('-t', '--token', dest='token',
                    help='access token from Facebook API')

args = parser.parse_args()

# Set the appropriate image type for PIL
img_type = "L"
if args.colour:
    img_type = "RGBA"

# Set the output filename
out_file = "output.jpg"
if args.outfile:
    out_file = args.outfile

# The number of image columns (width)
img_columns = 30
if args.width:
    img_columns = int(args.width)

# The number of image rows (height)
img_rows = 25
if args.height:
    img_rows = int(args.height)

# The Facebook Graph API access token
if args.token:
    access_token = args.token

# The pixel width of one image (50x50 with type=square)
img_width = 50

# The pixel height of one image (50x50 with type=square)
img_height = 50

# URL used to access friend information from account
FRIEND_URL = 'https://graph.facebook.com/me/friends?access_token=%s'

# URL to retrieve the profile picture from an account
PHOTO_URL = 'http://graph.facebook.com/%s/picture?type=square'

# MD5 Hashes of blank images
BLANK_HASHES = []
# MD5 Hash of the blank male image
BLANK_HASHES.append('af10cdc4144e0a16b097a293b0d95422')
# MD5 hash of the blank female image
BLANK_HASHES.append('04aaffaf075732616c0c35ae3e28bce6')

# Initial URL (before paging)
url = FRIEND_URL % access_token

# Complete friend list (from all pages)
friend_id_list = []

# Create initial canvas
img_canvas = Image.new(img_type, (img_width * img_columns, img_height * img_rows))


def get_json_data(url):
    """
    Retrieves the JSON response from Facebook and returns a parsed element.
    """
    urldata = urlopen(url)
    fh = urldata.read()

    return json.loads(fh)


def get_friends(json_data, friend_ids):
    """
    Takes the JSON data object and adds the friend IDs to a given list.
    """
    try:
        for friend in json_data["data"]:
            friend_ids.append(friend["id"])
    except KeyError:
        print "Error: Data element not found in response."
        if json_data["error"]:
            print "{0}: {1}".format(json_data["error"]["type"],
                                    json_data["error"]["message"])
        raise SystemExit(1)

    return friend_ids


print "Retrieving first page of friend results ..."
json_data = get_json_data(url)
friend_id_list = get_friends(json_data, friend_id_list)

while json_data is not None:
    try:
        print "Retrieving next page of friend results ..."
        url = json_data["paging"]["next"]
        json_data = get_json_data(url)
        friend_id_list = get_friends(json_data, friend_id_list)
    except KeyError:
        json_data = None

print "Friend retrieval complete, {0} friends found.".format(len(friend_id_list))

# Cache the images at the beginning so they don't have to download every use.
friend_images = []
print "Downloading profile pictures ..."
for x in friend_id_list:
    img_url = PHOTO_URL % x
    img_obj = cStringIO.StringIO(urlopen(img_url).read())
    # Avoid adding the blank images
    if md5(img_obj.getvalue()).hexdigest() not in BLANK_HASHES:
        friend_images.append(Image.open(img_obj))

# Build up the main canvas with randomly chosen images from the list.
for x in range(img_rows):
    for y in range(img_columns):
        img_canvas.paste(choice(friend_images), (y * img_width, x * img_height))

# Save the final image
print "Saving image to {0} ...".format(out_file)
img_canvas.save(out_file, "JPEG")
print "Process complete, image created."
