#!/usr/bin/env python
import eyeD3
from ogg import vorbis
from time import localtime
import json
import getopt
import sys
from email.mime.image import MIMEImage

def tag_mp3(target_file, info):
    try:
        tag = eyeD3.Tag()
        tag.link(target_file + '.mp3')
        tag.setVersion([2,3,0])
        tag.setArtist(str(info['artist']))
        tag.setAlbum(str(info['album']))
        tag.setTitle(str(info['title']))
        tag.setDate(localtime().tm_year)
        tag.setGenre(str(info['genre']))
        tag.addComment(str(info['comment']))
        tag.addImage(0x03, info['image'])
        tag.update()
    except:
        print "Cannot tag MP3 file"
        return

def tag_ogg(target_file, info):
    
    tag = vorbis.VorbisComment()
    tag['GENRE'] = str(info['genre'])
    tag['ALBUM'] = str(info['album'])
    tag['TITLE'] = str(info['title'])
    tag['COMMENTS'] = str(info['comment'])
    tag['ARTIST'] = str(info['artist'])
    tag['DATE'] = str(localtime().tm_year)
    tag['TRACKNUMBER'] = '1'

    # OK, now try importing the image
    try:
        fp = open(info['image'],'rb')
        img = MIMEImage(fp.read())
        tag['COVERARTMIME'] = img.get_content_type()
        tag['COVERART'] = (img.get_payload())
        tag['COVERART']
    except:
        print "Cannot open Image file"
        return

    if tag['COVERARTMIME']:
        try:
            target = target_file + '.ogg'
            tag.write_to(target) 
        except:
            print "Can't write to .ogg file"
            return

def main():

    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'h', ['json=', 'target='])
    except:
        print sys.exc_info()[0]
        sys.exit(2)

    json_file = None
    target_file = None
    for o, a in optlist:
        if o == '--json':
            json_file = a
        if o == '--target':
            target_file = a

    # Get the info from the tags.json file
    # FIXME: Make this a separate argument?
    if json_file:
        try:
            file = open(json_file, 'r')
            info = json.load(file)
            print info
        except:
            print sys.exc_info()[0]
            sys.exit(2)

    if target_file:
        tag_mp3(target_file, info)
        tag_ogg(target_file, info)

if __name__ == "__main__":
        main()
