#!/usr/bin/env python
"""
getimg.py

Gets the current image of the day from NASA and sets it as the
background in Gnome. The summary / description text is written
to the image.

Requires:
    PIL             (apt-get install python-imaging or pip install PIL)
    feedparser      (apt-get install python-feedparser or pip install feedparser)

Christian Stefanescu
http://0chris.com

Based on the bash script of Jessy Cowan-Sharp - http://jessykate.com
http://blog.quaternio.net/2009/04/13/nasa-image-of-the-day-as-gnome-background/

intelli_draw method from:
http://mail.python.org/pipermail/image-sig/2004-December/003064.html
"""
import Image
import ImageDraw
import ImageFont
import urllib
import feedparser
import os
import commands

# Configurable settings
DOWNLOAD_FOLDER = '~/.backgrounds/'
FONT_PATH = '/usr/share/fonts/truetype/ubuntu-font-family/Ubuntu-B.ttf'
FONT_SIZE = 20
# how many empty text rows should be inserted to overcome top panel overlap
EMPTY_ROWS = 3

# Don't change stuff beyond this point
FEED_URL = 'http://www.nasa.gov/rss/lg_image_of_the_day.rss'
font = ImageFont.truetype(FONT_PATH, FONT_SIZE)


def get_latest_entry():
    """
    Get URL and description of the latest entry in the feed
    """
    feed = feedparser.parse(FEED_URL)
    return (feed.entries[0].enclosures[0].href, feed.entries[0].summary)


def download_file(url):
    """
    Get the latest NASA image of the day from the feed, returns the name
    of the downloaded file.
    """
    remote_file = urllib.urlopen(url)
    local_name = url.split('/')[-1]
    local_path = os.path.expanduser(os.path.join(DOWNLOAD_FOLDER, local_name))
    local_file = open(local_path, 'w')
    local_file.write(remote_file.read())
    remote_file.close()
    local_file.close()
    return local_path


def intelli_draw(drawer, text, font, containerWidth):
    """
    Figures out how many lines (and at which height in px) are needed to print
    the given text with the given font on an image with the given size.

    Source:
    http://mail.python.org/pipermail/image-sig/2004-December/003064.html
    """
    words = text.split()
    lines = []
    lines.append(words)
    finished = False
    line = 0
    while not finished:
        thistext = lines[line]
        newline = []
        innerFinished = False
        while not innerFinished:
            if drawer.textsize(' '.join(thistext), font)[0] > containerWidth:
                newline.insert(0, thistext.pop(-1))
            else:
                innerFinished = True
        if len(newline) > 0:
            lines.append(newline)
            line = line + 1
        else:
            finished = True
    tmp = []
    for i in lines:
        tmp.append(' '.join(i))
    lines = tmp
    (width, height) = drawer.textsize(lines[0], font)
    return (lines, width, height)


def write_description(img_file, text):
    """
    Write the given text to the given imagefile and overwrite it.
    """
    img = Image.open(img_file)
    (img_width, img_height) = img.size
    draw = ImageDraw.Draw(img)
    lines, tmp, h = intelli_draw(draw, text, font, img_width)
    j = EMPTY_ROWS
    for i in lines:
        draw.text((0, 0 + j * h), i, font=font)
        j = j + 1
    img.save(open(img_file, 'w'), 'JPEG')


def set_gnome_wallpaper(file_path):
    command = "gconftool-2 --set \
            /desktop/gnome/background/picture_filename \
            --type string '%s'" % file_path
    status, output = commands.getstatusoutput(command)
    return status

if __name__ == '__main__':
    if not os.path.exists(os.path.expanduser(DOWNLOAD_FOLDER)):
        os.makedirs(os.path.expanduser(DOWNLOAD_FOLDER))
    (url, text) = get_latest_entry()
    img_file = download_file(url)
    write_description(img_file, text)
    status = set_gnome_wallpaper(img_file)

