#!/usr/bin/python

# Some notes about using this script:
# - Configure the application path and bundle id below
# - This script needs to be run as the user you need to set the checkmark for
# - The setting will not take effect until they log out and log back in at least once

import os.path
from Foundation import NSHomeDirectory, CFPreferencesCopyMultiple, CFPreferencesSetMultiple, kCFPreferencesAnyUser, kCFPreferencesCurrentHost, NSMutableDictionary, NSURL, NSURLBookmarkCreationMinimalBookmark, NSMutableArray

# --- CHANGE THESE SETTINGS ---
lowres_app_path = u'/Applications/TextEdit.app'
lowres_app_id   = u'com.apple.TextEdit'
# ----------------------------- 

# create the bookmark data
app_url = NSURL.alloc().initFileURLWithPath_(lowres_app_path)
bookmark, error = app_url.bookmarkDataWithOptions_includingResourceValuesForKeys_relativeToURL_error_(NSURLBookmarkCreationMinimalBookmark, [], None, None)

# check if the file exists already
ls_prefs = os.path.join(NSHomeDirectory(), u'Library/Preferences/com.apple.LaunchServices/com.apple.LaunchServices')
ls_prefs_plist = ls_prefs + u'.plist'

if os.path.isfile(ls_prefs_plist):
    # read it in
    current_prefs = CFPreferencesCopyMultiple(None, ls_prefs, kCFPreferencesAnyUser, kCFPreferencesCurrentHost)
else:
    # make a new dictionary
    current_prefs = NSMutableDictionary()

# Get any existing key or a new blank dict if not present
magnified = current_prefs.get(u'LSHighResolutionModeIsMagnified', NSMutableDictionary())
magnified_editable = NSMutableDictionary.dictionaryWithDictionary_(magnified)
# Build our values
options = NSMutableArray.alloc().init()
options.append(bookmark)
# A value of 3 = enabled, value of 2 = disabled
options.append(3)
magnified_editable[lowres_app_id] = options

# Update the setting
update_dict = NSMutableDictionary()
update_dict[u'LSHighResolutionModeIsMagnified'] = magnified_editable
result = CFPreferencesSetMultiple(update_dict, None, ls_prefs, kCFPreferencesAnyUser, kCFPreferencesCurrentHost)