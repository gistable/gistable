#!/usr/bin/python

'''Uses Cocoa classes via PyObjC to set a random desktop picture on all screens.
Tested on Mountain Lion and Mavericks.

See:
https://developer.apple.com/library/mac/documentation/cocoa/reference/applicationkit/classes/NSWorkspace_Class/Reference/Reference.html

https://developer.apple.com/library/mac/documentation/Cocoa/Reference/Foundation/Classes/NSURL_Class/Reference/Reference.html

https://developer.apple.com/library/mac/documentation/cocoa/reference/applicationkit/classes/NSScreen_Class/Reference/Reference.html
'''

import glob
import random

from AppKit import NSWorkspace, NSScreen
from Foundation import NSURL

pictures_glob = glob.glob("/Library/Desktop Pictures/*.jpg")
picture_path = random.choice(pictures_glob)

# generate a fileURL for the desktop picture
file_url = NSURL.fileURLWithPath_(picture_path)

# make image options dictionary
# we just make an empty one because the defaults are fine
options = {}

# get shared workspace
ws = NSWorkspace.sharedWorkspace()

# iterate over all screens
for screen in NSScreen.screens():
    # tell the workspace to set the desktop picture
    (result, error) = ws.setDesktopImageURL_forScreen_options_error_(
                file_url, screen, options, None)