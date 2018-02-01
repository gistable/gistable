#! /usr/bin/env python

import xml.etree.ElementTree as ET
import sys
import base64
import os
import StringIO
from PIL import Image


PREFIX_PNG = "data:image/png;base64,"
PREFIX_JPG = "data:image/jpg;base64,"
ATTR = "{http://www.w3.org/1999/xlink}href"
DEFAULT_NS = "http://www.w3.org/2000/svg"

with open(sys.argv[1]) as svgfile:
    root = ET.parse(svgfile)
    file_id = 1
    base_name = os.path.splitext(sys.argv[1])[0]
    for e in root.findall(".//{%s}image" % DEFAULT_NS):
        href = e.get(ATTR)
        if href and href.startswith(PREFIX_PNG):
            pngimage = StringIO.StringIO()
            jpgimage = StringIO.StringIO()
            pngimage.write(base64.b64decode(href[len(PREFIX_PNG):]))
            Image.open(pngimage).save(jpgimage, "JPEG")
            e.set(ATTR, PREFIX_JPG + base64.b64encode(jpgimage.getvalue()))

root.write(sys.argv[1])
