#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from gimpfu import *

def plugin_main(img, layer):
    width = img.width
    height = img.height
    
    resizedWidth = width / 2
    resizedHeight = height / 2
    
    name = ""
    if img.filename:
        name = os.path.basename(img.filename)
    
    pdb.gimp_image_scale(img, resizedWidth, resizedHeight)
    
    gimp.message(
       "Original Size: %d,%d\n" % (width, height) +
       "Resized Size: %d,%d\n\n" % (resizedWidth, resizedHeight) +
       "CSS: \nwidth: %dpx;\nheight: %dpx;\n\n" % (resizedWidth, resizedHeight) +
       "img: <img src=\"%s\" width=\"%d\" height=\"%d\" />" % (name, resizedWidth, resizedHeight)
       )

register(
        "python_fu_scale_half",
        "Scale the image to the half size",
        "Scale the image to the half size",
        "Yoichi Imai",
        "Yoichi Imai",
        "2014",
        "<Image>/Image/Scale to Half Size",
        "*",
        [],
        [],
        plugin_main)

main()
