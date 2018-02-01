#!/usr/bin/python

# Copyright (c) 2016 University of Utah Student Computing Labs. ################
# All Rights Reserved.
#
# Permission to use, copy, modify, and distribute this software and
# its documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appears in all copies and
# that both that copyright notice and this permission notice appear
# in supporting documentation, and that the name of The University
# of Utah not be used in advertising or publicity pertaining to
# distribution of the software without specific, written prior
# permission. This software is supplied as is without expressed or
# implied warranties of any kind.
################################################################################

# report_critical_update_versions.py ###########################################
# 11/23/16, v0.3, todd.mcdaniel@utah.edu
#
# more of a learning experience than a useful product.
# ported from an applescript found here:
# https://www.jamf.com/jamf-nation/discussions/19111/xprotect-status-extension-attribute
# parses update versions, some managed by `sudo softwareupdate --background-critical`
#
################################################################################

import datetime
import os
import subprocess

def main():

    # format for update description:
    # update title, file for date calculation, file for version discovery, version command to use

    updates = [
        ["XProtect", "/System/Library/CoreServices/XProtect.bundle/Contents/Resources/XProtect.meta.plist", "/System/Library/CoreServices/XProtect.bundle/Contents/Resources/XProtect.meta.plist", "Version"],
        ["Gatekeeper", "/private/var/db/gkopaque.bundle/Contents/version.plist", "/private/var/db/gkopaque.bundle/Contents/version.plist", "CFBundleShortVersionString"],
        ["SIP", "/System/Library/Sandbox/Compatibility.bundle/Contents/version.plist", "/System/Library/Sandbox/Compatibility.bundle/Contents/version.plist", "CFBundleShortVersionString"],
        ["MRT", "/System/Library/CoreServices/MRT.app/Contents/version.plist", "/System/Library/CoreServices/MRT.app/Contents/version", "CFBundleShortVersionString"],
        ["Core Suggestions", "/System/Library/Intelligent Suggestions/Assets.suggestionsassets/Contents/version.plist", "/System/Library/Intelligent Suggestions/Assets.suggestionsassets/Contents/version.plist", "CFBundleShortVersionString"],
        ["Incompatible Kernel Ext.", "/System/Library/Extensions/AppleKextExcludeList.kext/Contents/version.plist", "/System/Library/Extensions/AppleKextExcludeList.kext/Contents/version", "CFBundleShortVersionString"],
        ["Chinese Word List", "/usr/share/mecabra/updates/com.apple.inputmethod.SCIM.bundle/Contents/version.plist", "/usr/share/mecabra/updates/com.apple.inputmethod.SCIM.bundle/Contents/info", "SUVersionString"],
        ["Core LSKD (dkrl)", "/usr/share/kdrl.bundle/info.plist", "/usr/share/kdrl.bundle/info", "CFBundleVersion"]
    ]

    print("{:<24} {} {:>12}".format("Name", "Date", "Version"))
    print("_" * 42)

    for index, data in enumerate(updates):
        version_number = ""
        try:
            mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(data[1]))
            formatted_modtime = mod_time.strftime('%Y.%m.%d')

            try:
                version_string = subprocess.check_output(["defaults", "read", data[2], data[3]])
                version_number = version_string.split("\n")[0]
            except:
                pass
        except:
            formatted_modtime = "missing?"

        print("{:<24} {} {:>6}".format(data[0], formatted_modtime, version_number))

if __name__ == '__main__':
    main()