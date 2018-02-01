# Copyright 2012 Joseph R. Hunt
# All rights reserved.

# This is just a quick hack and is not reliable
# width 850,315

import re
import urllib
import Image
import cStringIO
from oauth_hook import OAuthHook
import requests

baseurl = "http://apod.nasa.gov/apod/"
indexurl = baseurl + "astropix.html"
regex = "a href=\"(image.*)\""
imgsize = 1000, 1000
twitterurl = "http://api.twitter.com/1/"

# set all of these
OAuthHook.consumer_key = ''
OAuthHook.consumer_secret = ''
access_token = ''
access_token_secret = ''


oauth_hook = OAuthHook(access_token, access_token_secret, header_auth=True)


def get_apod_image():
    apodpage = urllib.urlopen(indexurl).read()  # grab the mainpage
    apod_url = re.search(regex, apodpage).group(1)  # find image url
    imgfile = urllib.urlopen(baseurl + apod_url)  # open the image file
    imgstr = cStringIO.StringIO(imgfile.read())  # parse it into memory (cStringIO is faster than StringIO)
    img = Image.open(imgstr)
    img.convert("RGB")
    img.thumbnail(imgsize, Image.ANTIALIAS)
    img.save("apod.png", "PNG", optimize=True)


def update_twitter():
    client = requests.session(hooks={'pre_request': oauth_hook})
    image = open('apod.png', 'rb')
    response = client.post(twitterurl + 'account/update_profile_background_image.json', files={'image': ('apod.png', image)})
    print response

if __name__ == '__main__':
    get_apod_image()
    update_twitter()