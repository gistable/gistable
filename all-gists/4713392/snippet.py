#!/usr/bin/env python
# coding=utf-8

# pip install kurt
# python thumb.py 3013900.sb

import sys
import kurt
from kurt.files import ScratchProjectFile, ScratchSpriteFile

def save_thumb(project):
    project.load()
    thumb = project.info["thumbnail"]
    if thumb:
        thumb.save("thumbnail.png")
    
if __name__ == '__main__':
    if len(sys.argv) < 2:
        exit

    project = ScratchProjectFile(sys.argv[1], load=False)
    try:
        save_thumb(project)
    except FolderExistsException, e:
        print "Folder exists: %s" % unicode(e)
    except FileNotFoundException, e:
        print "File missing: %s" % unicode(e)
    except InvalidProject, e:
        print "Invalid project: %s" % unicode(e)