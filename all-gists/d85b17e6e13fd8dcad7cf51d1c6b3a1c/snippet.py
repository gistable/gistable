#!/usr/bin/python

# Credit to frogor for the objc

from Foundation import NSBundle
import json
import objc
import os
import plistlib
import subprocess

IOKit = NSBundle.bundleWithIdentifier_('com.apple.framework.IOKit')
functions = [('KextManagerCopyLoadedKextInfo', '@@@'), ]
objc.loadBundleFunctions(IOKit, globals(), functions)

kernel_dict = KextManagerCopyLoadedKextInfo(None, None)
folderpaths = ['/Applications', '/Users', '/System/Library/Extensions',
               '/Library']

unidentifiedKexts = []

# This just finds all of the currently loaded kexts.
identifiedKexts = \
    [
        {
            'Identifier': kernel_dict[kext]['CFBundleIdentifier'],
            'KextPath': kernel_dict[kext]['OSBundlePath'],
            'Version': kernel_dict[kext]['CFBundleVersion'],
        }
        for kext in kernel_dict.keys()
        if not kext.startswith(('__kernel', 'com.apple'))
    ]

# This checks common folder paths for any unloaded Kexts and attempts to give
# the same type of info as above. This can take a really long time to finish,
# and could really piss people off if you run this more than once.
# More notes:
# mdfind by default doesn't search hidden paths or application bundles
#
# kextfind can't traverse folders
#
# locate takes just as long as os.walk if not longer since we are skipping some
# of the folders. If we use locate, the db could also be out of date.
#
# COMMENT THIS OUT IF YOU DON'T CARE ABOUT THIS AND ONLY WANT LOADED KEXTS!
# """
for path in folderpaths:
    for root, dirnames, filesnames in os.walk(path):
        if root.endswith('.kext'):
            infoplist = os.path.join(root, 'Contents/Info.plist')
            if os.path.isfile(infoplist):
                kextplistpath = plistlib.readPlist(infoplist)
                if 'apple' in kextplistpath['CFBundleIdentifier']:
                    continue
                else:
                    kextinfo = {
                        'Identifier': kextplistpath['CFBundleIdentifier'],
                        'KextPath': root,
                        'Version': kextplistpath['CFBundleVersion'],
                    }
                    identifiedKexts.append(kextinfo)
            else:
                unidentifiedKexts.append(root)
# COMMENT THIS OUT IF YOU DON'T CARE ABOUT THIS AND ONLY WANT LOADED KEXTS!
# """

kextsThatWillMakeAnAdminCry = {'IdentifiedKexts': identifiedKexts,
                               'UnidentifiedKexts': unidentifiedKexts}

print json.dumps(kextsThatWillMakeAnAdminCry, indent=4, sort_keys=True)
