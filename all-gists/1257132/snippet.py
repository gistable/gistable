#!/usr/bin/python

"""
This is a handy script to download the media from General Conference
for your own use.  Modify the options below, starting with DOWNLOAD_
to download the files you wish.

The only non-Python standard library dependency is BeautifulSoup.
"""

import sys
import urllib
import urlparse

from BeautifulSoup import BeautifulSoup

# Don't actually download files, just show what will be downloaded
DRYRUN = False

CONFERENCE_URL = "http://lds.org/general-conference/sessions/2011/10?lang=eng"

# Possible types:
#  video-360p
#  video-720p
#  video-1080p
#  video-wmv
#  audio-mp3
#  audio-m4b - Only for entire sessions
DOWNLOAD_CLASS = "video-1080p"

# Download indvidual talks and musical numbers (if downloading music)?
DOWNLOAD_INDIVIDUAL = True
# Download musical numbers?
DOWNLOAD_MUSIC = False
# Download files for entire sessions?
DOWNLOAD_SESSIONS = False
# Download Priesthood session?
DOWNLOAD_PRIESTHOOD = True
# Download the General Young Women's meeting files?
DOWNLOAD_YOUNG_WOMEN_MEETING = False
# Download the General Relief Society meeting files?
DOWNLOAD_RELIEF_SOCIETY_MEETING = False

def main():
    """
    I really probably should take command-line parameters for the
    configuration, but oh well.
    """

    # Sanity checking:
    if not (DOWNLOAD_SESSIONS or DOWNLOAD_INDIVIDUAL):
        print "Must either download sessions or talks or both"
        sys.exit(1)

    if (not DOWNLOAD_SESSIONS) and DOWNLOAD_CLASS == "audio-m4b":
        print "m4b is only available for full sessions, \
    must have DOWNLOAD_SESSIONS selected"
        sys.exit(1)

    if (not DOWNLOAD_INDIVIDUAL) and DOWNLOAD_MUSIC:
        print "To download music, must download individual"
        sys.exit(1)

    page = urllib.urlopen(CONFERENCE_URL)
    document = BeautifulSoup(page)

    download_tags = document.findAll("a", attrs={"class": DOWNLOAD_CLASS})

    for tag in download_tags:
        href = tag.attrMap["href"]

        # Don't donwload Young Women Meeting files if not wanted
        if not DOWNLOAD_YOUNG_WOMEN_MEETING and \
           tag.findParents(attrs={"class": "sessions", "id": "young-women"}):
            continue

        # Don't donwload Young Women Meeting files if not wanted
        if not DOWNLOAD_RELIEF_SOCIETY_MEETING and \
           tag.findParents(attrs={"class": "sessions", "id": "relief-society"}):
            continue

        # Don't donwload Priesthood Session files if not wanted
        if not DOWNLOAD_PRIESTHOOD and \
           tag.findParents(attrs={"class": "sessions", "id": "priesthood"}):
            continue

        # Don't download full session files if not wanted
        if not DOWNLOAD_SESSIONS and \
           tag.findParents(attrs={"class": "head-row"}):
            continue

        # Don't download individual files if not wanted
        if not DOWNLOAD_INDIVIDUAL and \
           not tag.findParents(attrs={"class": "head-row"}):
            continue

        # Don't download musical number files if not wanted
        if not DOWNLOAD_MUSIC and \
           tag.findParents(attrs={"class": "music"}):
            continue

        # Get an appropriate filename
        filename = urlparse.urlsplit(href).path.split("/")[-1]
        print "Downloading %s as %s" % (href, filename)

        if not DRYRUN:
            urllib.urlretrieve(href, filename)


if __name__ == "__main__":
    main()
