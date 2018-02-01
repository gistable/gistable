#!/usr/bin/env python
#-*- coding:utf-8 -*-

import commands
import os.path
from sys import argv

def set_gnome_wallpaper(file_path):
    command = "gconftool-2 --set \
            /desktop/gnome/background/picture_filename \
            --type string '%s'" % file_path
    status, output = commands.getstatusoutput(command)
    return status



if __name__ == '__main__':
    if len(argv) <= 1:
        print "usage: %s img_path" % argv[0]
    else:
        img_path = os.path.abspath(argv[1])
        if not set_gnome_wallpaper(img_path):
            print "Wallpaper changed with success."
        else:
            print "An error ocurred while setting a new wallpaper."
