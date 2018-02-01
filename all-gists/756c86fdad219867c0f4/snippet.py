#!/usr/bin/env python

# install imagesize: pip install imagesize

__author__ = 'Olivier Pieters'
__author_email__ = 'me@olivierpieters.be'
__license__ = 'BSD-3-Clause'

import yaml, imagesize
from os import listdir, rename
from os.path import isfile, join

# configuration
output_file = "ghent-light-festival.yml"
input_file = output_file
image_path = "ghent-light-festival"
extensions= ['jpg', 'png']

# set correct path
path = join("../../assets/photography/", image_path)

# extract image files
print('Collecting files...')
files = [f for f in listdir(path) if isfile(join(path, f))]
files = [f for f in files if f[f.rfind('.')+1:] in extensions ]

# rename image files
print('Renaming files...')
new_files = []
for f in files:
    if f[f.rfind('-')+1:f.rfind('.')] != 'thumbnail':
        newf = f[:f.rfind('-')] + "-%sx%s" % imagesize.get(join(path, f)) + f[f.rfind('.'):]
        rename(join(path, f),join(path, newf))
    else:
        newf = f
    new_files.append(newf)

files = new_files

# helper objects to store gallery data
new_gallery = {}
thumbs = {}

# group gallery data
print('Grouping files...')
for f in files:
    filename = f[:f.rfind('-')]
    if f[f.rfind('-')+1:f.rfind('.')] == "thumbnail":
        thumbs[filename] = f
    else:
        if filename in new_gallery:
            new_gallery[filename].append(f)
        else:
            new_gallery[filename] = [f]

# find largest image -> set as original
print('Searching for originals and missing thumbnails...')
originals = {}
for image_set in new_gallery:
    max_width, max_height = imagesize.get(join(path, new_gallery[image_set][0]))
    min_width, min_height = imagesize.get(join(path, new_gallery[image_set][0]))
    original = new_gallery[image_set][0]
    thumbnail = new_gallery[image_set][0]
    for image in new_gallery[image_set]:
        width, height = imagesize.get(join(path, image))
        if (width*height) > (max_width*max_height):
            original = image
        if (width*height) < (min_width*min_height):
            thumbnail = image
    # delete original from list to avoid double entries
    del new_gallery[image_set][new_gallery[image_set].index(original)]
    originals[image_set] = original
    # add thumbnial if not yet in dict (not removed since might still be useful)
    if image_set not in thumbs:
        thumbs[image_set] = thumbnail

# try to load YAML data
print('Checking existing YAML data...')
if isfile(input_file):
    input_gallery = yaml.load(open(input_file, 'r'))
else:
    # create empty dummy file
    input_gallery = {"pictures": []}

old_gallery = input_gallery['pictures']

# merge two data sets into one
print('Merging YAML data...')
for pic in new_gallery:
    found = False
    # try to find matching filename
    for i in old_gallery:
        if pic == i["filename"]:
            i["sizes"] = new_gallery[pic]
            # include thumbnail if present
            if pic in thumbs:
                i["thumbnail"] = thumbs[pic]
            found = True
    if not found:
        # create new entry
        old_gallery.append({"filename": pic, "sizes": new_gallery[pic], "thumbnail": thumbs[pic], "original": originals[pic]})

# check if path existing
if "picture_path" not in input_gallery:
    input_gallery["picture_path"] = image_path

# write to output file
print('Writing YAML data to file...')
with open(output_file, 'w') as f:
    f.write( yaml.dump(input_gallery, default_flow_style=False) )
