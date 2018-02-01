#!/usr/bin/env python
#
# Google Cardboard Camera extractor
# Extracts audio and second image from the XMP header in Cardboard Camera images
# Requires python-xmp-toolkit ( pip install python-xmp-toolkit )
#
# Usage:
# $ carboardcam_extract.py myimage_vr.jpg
#
# Creates two new files - myimage_vr_audio.mp4 and myimage_vr_righteye.jpg
#
# License: MIT
# Copyright (c) 2015 Andrew Perry
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import sys
from os import path
from base64 import b64decode
from libxmp.utils import file_to_dict

img_filename = sys.argv[1]
xmp = file_to_dict(img_filename)

audio_b64 = xmp[u'http://ns.google.com/photos/1.0/audio/'][1][1]

afh = open(path.splitext(img_filename)[0]+"_audio.mp4", 'wb')
afh.write(b64decode(audio_b64))
afh.close()

image_b64 = xmp[u'http://ns.google.com/photos/1.0/image/'][1][1]

ifh = open(path.splitext(img_filename)[0]+"_righteye.jpg", 'wb')
ifh.write(b64decode(image_b64))
ifh.close()
