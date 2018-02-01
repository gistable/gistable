#!/usr/bin/python

""" Graham Gilbert 5/1/16
Change TARGET_APP and the app name on line 53 to your chosen app to quit.
Run this as often as you'd like via a launchagent.

No warranty expressed or implied. If things go kaboom, it's your problem!
"""

from AppKit import NSWorkspace
import subprocess
import plistlib
import os
import sys
import datetime

TARGET_APP = 'Clear'
PLIST_PATH = os.path.join(os.path.expanduser("~"), 'Library', 'Preferences', 'app_open.plist')
# Run this script every minute

def main():

    open_apps = NSWorkspace.sharedWorkspace().runningApplications()

    # see if the app is open, if not we're going to remove the plist
    app_open = False
    for app in open_apps:
        if TARGET_APP == app.localizedName():
            app_open = True

    if app_open == False:
        if os.path.exists(PLIST_PATH):
            os.remove(PLIST_PATH)
        sys.exit()

    if os.path.exists(PLIST_PATH):
        # plist exists, read it
        plist_data = plistlib.readPlist(PLIST_PATH)
    else:
        plist_data = {}
    # App is open, is it frontmost?
    active_app = NSWorkspace.sharedWorkspace().frontmostApplication().localizedName()
    now = datetime.datetime.now()
    if TARGET_APP == active_app:
        plist_data['last_active'] = now
        plistlib.writePlist(plist_data, PLIST_PATH)
        sys.exit()
    else:
        # it's not frontmast, when was the last time we saw it?
        if 'last_active' not in plist_data:
            # covering ourselves if it's not been recorded before
            plist_data['last_active'] = now
            plistlib.writePlist(plist_data, PLIST_PATH)
            sys.exit()
        if plist_data['last_active'] < now-datetime.timedelta(minutes=5):
            # app hasb't been active for five minutes
            subprocess.call(['/usr/bin/osascript', '-e', 'tell application "Clear" to quit'])
            os.remove(PLIST_PATH)


if __name__ == '__main__':
    main()
