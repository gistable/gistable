#!/usr/bin/env python2.6

import sys, os, fnmatch, subprocess

image_dir = ''.join(sys.argv[1:])
optipng = '/usr/bin/optipng' 
jpegtran = '/usr/local/bin/jpegtran' 

pngs = jpgs = []
pngs_size = jpgs_size = pngs_size_new = jpgs_size_new = 0

# Exit if invalid image directory
if not os.path.exists(image_dir):
  print 'Invalid path. Exiting.'
  sys.exit()

# Find PNGs and JPGs and add up filesize
for root, dirnames, filenames in os.walk(image_dir):
  for filename in fnmatch.filter(filenames, '*.png'):
    image = os.path.join(root, filename)
    pngs.append(image)
    pngs_size += os.path.getsize(image)

  for filename in fnmatch.filter(filenames, '*.jpg'):
    image = os.path.join(root, filename)
    jpgs.append(image)
    jpgs_size += os.path.getsize(image)

# Run
for image in pngs:
  subprocess.call(["optipng", image])
  pngs_size_new += os.path.getsize(image)

for image in jpgs:
  subprocess.call(["jpegtran", "-optimize", "-copy", "all", "-outfile", image, image])
  jpgs_size_new += os.path.getsize(image)

# Calculation
png_savings = pngs_size - pngs_size_new
jpg_savings = jpgs_size - jpgs_size_new

print '*****'
print 'PNG savings bytes: ' + str(png_savings)
print 'PNG savings percentage: ' + str(float(png_savings) / pngs_size * 100) + '%'

print 'JPG savings bytes: ' + str(jpg_savings)
print 'JPG savings percentage: ' + str(float(jpg_savings) / jpgs_size * 100) + '%'
print '-----'
print 'Total savings bytes: ' + str(png_savings + jpg_savings) 
print 'Total savings percentage: ' + str( float(png_savings + jpg_savings) / (pngs_size + jpgs_size) * 100 ) + '%' 
print '*****'
