#!/usr/bin/python

##  Script:     get_chrome_extensions.py
##  Author:     Christopher Collins (christophercollins@livenation.com)
# also, owen wuz here. minor corrections (utf-8)
###########################################
##Description: This script searches the last logged in user's installed extensions and submits it to Casper during an inventory report.
###########################################

import os
import json
from Foundation import CFPreferencesCopyAppValue
from SystemConfiguration import SCDynamicStoreCopyConsoleUser
import sys

#Get name of last logged in user so the extension attribute will report information for the user even if they aren't logged in"

username = (SCDynamicStoreCopyConsoleUser(None, None, None) or [None])[0]
lastloggedinuser = [username, ""][username in [u"loginwindow", None, u""]]
userchromepath = '/Users/' + lastloggedinuser + '/Library/Application Support/Google/Chrome/'

#Initialize a dictionary to hold the variable names extension developers used if developers localized their extension
internationalized_extensions = {}

#Initialize a directory to hold the names of the installed extensions
installed_extensions = []

#walk the chrome application support folder
for (dirpath, dirnames, filenames) in os.walk(userchromepath):

    #Test to see if file is a manifest.json file and then check its name if it is a placeholder name for a localization file (has __MSG)
    #If it is a normal name, then add it to the final list. If its not, add it to the internationalized_extensions dictionary to match against a localized messages.json file
    for file in filenames:
        if ("Extensions" in dirpath and "manifest.json" in file):
            manifest = json.load(open(os.path.join(dirpath, file)))
            extension_name = manifest.get('name')
            name = extension_name
            if '__MSG_'not in extension_name:
                installed_extensions.append(extension_name)
            else:
                extension_name = extension_name[6:-2]
                if extension_name not in internationalized_extensions:
                    internationalized_extensions[extension_name] = extension_name
        else:
            if (("Extensions" and "locales/en" in dirpath) and "messages.json" in file):
                manifest = json.load(open(os.path.join(dirpath, file)))
                if manifest:
                    for key in internationalized_extensions.keys():
                        if manifest.get(key):
                            extension_name = manifest.get(key).get('message')
                            installed_extensions.append(extension_name)
                        else:
                            if manifest.get(key.lower()):
                                extension_name = manifest.get(key.lower()).get('message')
                                installed_extensions.append(extension_name)
print "<result>{}</result>".format(', '.join(sorted(list(set(installed_extensions)))).encode('utf-8'))
