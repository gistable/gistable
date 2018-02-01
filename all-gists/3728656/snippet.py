#!/usr/bin/python
#
# Usage: python paste_img.py dest_file.png
#
# This program readd the image stored in the clipboard, and dumps it into a file

import gtk, pygtk
pygtk.require('2.0')
import sys

dest_file = sys.argv[1]

clipboard = gtk.clipboard_get()
image = clipboard.wait_for_image()
image.save(dest_file, dest_file.split(".")[-1])
