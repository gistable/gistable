#!/usr/bin/env python

# Simple Image Diffs
# ==================
#
# How to Install
# --------------
#
# Download the script somewhere on $PATH as 'simple-imagediff' with +x:
#
# $ cd ~/bin
# $ wget -O simple-imagediff https://raw.github.com/gist/1716699/simple-imagediff.py
# $ chmod +x simple-imagediff
#
# Prerequisites
# -------------
#
# The script should work out-of-the box on Ubuntu 11.10. On other OS'es you may
# need to install PIL and Gtk3.
#
# Git Setup
# ---------
#
# In ~/.gitconfig, add:
#
# [diff "image"]
#   command = simple-imagediff
#
# In your project, create .gitattributes file and add (this enables the custom
# diff tool above):
#
# *.gif diff=image
# *.jpg diff=image
# *.png diff=image
#
# Try It
# ------
#
# $ git diff path/to/file.png
#
# NOTE: file.png must be versioned and the working copy must be different.

import os
import sys

import Image

from gi.repository import Gdk, Gtk

class SimpleImageDiffWindow(Gtk.Window):
    def __init__(self, left, right):
        Gtk.Window.__init__(self, title="Simple Image Diff (%s, %s)" % (left, right))
        self.set_default_size(640, 480)
        align = Gtk.Alignment()
        align.set_padding(10, 10, 10, 10)
        box = Gtk.HBox(homogeneous=True, spacing=10)
        box.add(self._create_image_box(left))
        box.add(self._create_image_box(right))
        align.add(box)
        self.add(align)
        self.resize(1, 1)
        self.set_position(Gtk.WindowPosition.CENTER)

    def _create_image_box(self, image_file):
        box = Gtk.VBox(spacing=10)
        frame = Gtk.Frame()
        image = Gtk.Image()
        image.set_from_file(image_file)
        title = Gtk.Label(label="W: %dpx  |  H: %dpx" % Image.open(image_file).size)
        frame.add(image)
        box.pack_start(frame, True, True, 0)
        box.pack_end(title, False, False, 10)
        return box

def _halt(message, code):
    sys.stderr.write("[ERROR] %s\n" % message)
    sys.exit(0 << code)

def _verify_file_exists(target):
    if not os.path.exists(target):
        _halt("The file '%s' does not exists." % target, 2)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        _halt('Not enough arguments.', 1)
    _verify_file_exists(sys.argv[1])
    _verify_file_exists(sys.argv[2])
    app = SimpleImageDiffWindow(sys.argv[1], sys.argv[2])
    app.connect('delete-event', Gtk.main_quit)
    app.show_all()
    Gtk.main()