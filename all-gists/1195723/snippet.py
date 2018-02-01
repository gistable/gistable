#!/usr/bin/env python

import plistlib
import json
import tkFileDialog
import re
import sys

file_to_open = tkFileDialog.askopenfilename(message="Select an existing plist or json file to convert.")
converted = None

if file_to_open.endswith('json'):
    converted = "plist"
    converted_dict = json.load(open(file_to_open))
    file_to_write = tkFileDialog.asksaveasfilename(message="Select a filename to save the converted file.",
                                                   defaultextension = converted)
    plistlib.writePlist(converted_dict, file_to_write)
elif file_to_open.endswith('plist'):
    converted = "json"
    converted_dict = plistlib.readPlist(file_to_open)
    converted_string = json.dumps(converted_dict, sort_keys=True, indent=4)
    file_to_write = tkFileDialog.asksaveasfilename(message="Select a filename to save the converted file.",
                                                   defaultextension = converted)
    open(file_to_write, 'w').write(converted_string)
else:
    print("WHAT THE F*** ARE YOU TRYING TO DO??????")
    sys.exit(1)
