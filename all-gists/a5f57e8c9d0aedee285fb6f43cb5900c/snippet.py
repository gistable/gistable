#!/usr/bin/env python

import numpy as np
import cv2
from sys import argv

# Gaussian radius (should really be an argument):
r = 21

src, dst = argv[1:]

def get_sharpness(img):
  img = img.mean(axis=2)
  blurred = cv2.GaussianBlur(img, (r, r), 0)
  sharp = np.abs(img - blurred)
  return sharp

viddy = cv2.VideoCapture(src)

width = int(viddy.get(3)) # can you tell this API is by C programmers?
height = int(viddy.get(4))
frame_count = int(viddy.get(7))

best_pixels = np.empty((height, width, 3)) # 3 channels
best_sharpness = get_sharpness(best_pixels)

for frame_n in range(frame_count):
  print "%s/%s" % (frame_n, frame_count)

  okay, frame = viddy.read()
  if not okay: break
  
  if frame_n == 0:
    best_pixels = frame
  
  sharpness = get_sharpness(frame)
  better_indexes = np.where(sharpness > best_sharpness)
  
  best_pixels[better_indexes] = frame[better_indexes]
  best_sharpness[better_indexes] = sharpness[better_indexes]

cv2.imwrite(dst, best_pixels)