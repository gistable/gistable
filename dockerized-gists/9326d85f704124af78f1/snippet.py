#!/usr/bin/python

import os
import subprocess
import glob

image_format = "png"

# Get the paths to all icon files in the CoreTypes bundle
coretypes_path = '/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources'
coretypes_icon_pattern = os.path.join(coretypes_path, '*.icns')
coretypes_icon_paths = glob.glob(coretypes_icon_pattern)

# Process each icon file path
for coretypes_icon_path in coretypes_icon_paths:
    # Each icon file serves as the input
    input_file_path = coretypes_icon_path
    # Get the base name of the icon file and split off its extension
    coretype_icon_basename = os.path.basename(coretypes_icon_path)
    coretype_icon_name = os.path.splitext(coretype_icon_basename)[0]
    output_dirname = os.path.expanduser('~/Pictures/CoreTypesIcons')
    if not os.path.isdir(output_dirname):
        os.makedirs(output_dirname)
    output_file_name = "{0}.png".format(coretype_icon_name)
    output_file_path = os.path.join(output_dirname, output_file_name)
    if os.path.isfile(output_file_path):
        # File exists, skip
        print('File {0} exists.'.format(output_file_name))
    else:
        # Plug in values into the convert command
        convert_msg = "Converting file {0} to {1}.".format(coretype_icon_basename,
                                                           output_file_name)
        print(convert_msg)
        convert_cmd = ['/usr/bin/sips',
                       '--setProperty',
                       'format',
                       image_format,
                       '--resampleHeightWidthMax',
                       '128',
                       input_file_path,
                       '--out',
                       output_file_path]
        subprocess.call(convert_cmd)
