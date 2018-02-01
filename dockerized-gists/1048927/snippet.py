#! /usr/bin/env python
import os, sys
paths = ["/Applications/Microsoft Office 2011/",
"/Applications/Remote Desktop Connection",
"/Applications/Microsoft Communicator",
"/Applications/Microsoft Messenger",
"/Users/username/Library/Preferences/Microsoft/Office 2011/",
"/~/Library/Application Support/Microsoft/",
"/~/Documents/Microsoft User Data/",
"/Library/Automator",
"/Library/Application Support/Microsoft/MAU2.0/",
"/Library/Application Support/Microsoft/MERP2.0/",
"/Library/Fonts/Microsoft",
"/Library/Preferences/com.microsoft.office.licensing.plist",
"/Library/LaunchDaemons/com.microsoft.office.licensing.helper.plist",
"/Library/PrivilegedHelperTools/com.microsoft.office.licensing.helper",
# "/Library/Internet Plug-Ins/<all SharePoint files>
"/var/db/receipts/com.microsoft.office.*"
]

for path in paths:
    os.system("sudo rm -rf %s" % path)