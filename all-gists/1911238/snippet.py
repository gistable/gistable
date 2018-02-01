#!/usr/bin/env python

import sys
import os
import eyeD3

tag = eyeD3.Tag()

for arg in sys.argv[1:]:
  tag.link(os.path.abspath(arg))
  lyrics = open(os.path.splitext(os.path.abspath(arg))[0] + ".txt", "r").read()
  tag.addLyrics(lyrics)
  tag.update()
