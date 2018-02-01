#!/usr/bin/python
# encoding: utf-8
#
# Arjen van Bochoven Oct 2014
# Script to rebrand/customize Managed Software Center
#
# Prerequisites: You need Xcode (5/6) installed
# For Xcode 6 you need to add the 10.8 SDK
# See: https://github.com/munki/munki/wiki/Building%20Munki2%20Pkgs
#
# Put this script in an *empty* directory
# and make it executable
# 
# Set textToReplace to your preferred name
# Add an optional AppIcon.icons file
# Add an optional postflight_script
# 
# Then run ./munki_rebrand.py
# 
# ! Caveat: this is a very rudimentary script that is likely
# to break in future MSC releases. Use at your own risk

import fileinput
import subprocess
from os import listdir, stat, chmod
from os.path import isfile, join
from shutil import copyfile

# This is the name Manage Software Center will get
# Does *not* work with unicode characters
textToReplace = "Greg's Amazing Cookiejar"

# Text to search (don't change this)
textToSearch = 'Managed Software Center'

# Optional icon file to replace the MSC icon
srcIcon = 'AppIcon.icns'

# Optional postinstall script to be executed upon install
postinstall_script = 'postinstall_script'

# Git release tag (leave empty for latest build)
tag = 'v2.0.1'

# Git repo
git_repo = "https://github.com/munki/munki"

# First cleanup previous runs
print 'Cleaning up previous runs'
proc = subprocess.Popen(['sudo','/bin/rm','-rf', 'munki'])
proc.communicate()

# Checkout git repo
print 'Cloning git repo'
proc = subprocess.Popen(['git','clone', git_repo])
proc.communicate()

if tag:
	print 'Checkout tag %s' % tag
	proc = subprocess.Popen(['git','-C', 'munki', 'checkout', 'tags/%s' % tag])
	proc.communicate()

print "Replacing %s with %s" % (textToSearch, textToReplace.encode('utf-8'))
# List of filenames that we need to process
replaceList = ['InfoPlist.strings', 'Localizable.strings', 'MainMenu.strings']

# List of files with text replacements
files = []

# App directories
appDirs = ['munki/code/apps/Managed Software Center/Managed Software Center',\
			'munki/code/apps/MunkiStatus/MunkiStatus']

for appDir in appDirs:
	if isfile(join(appDir, 'en.lproj/MainMenu.xib')):
		files.append(join(appDir,'en.lproj/MainMenu.xib'))

	if isfile(join(appDir, 'MSCMainWindowController.py')):
		files.append(join(appDir,'MSCMainWindowController.py'))

	# Find all directories ending in .lproj
	for f in listdir(appDir):
		if f.endswith('.lproj'):
			for i in replaceList:
				if isfile(join(appDir, f, i)):
					files.append(join(appDir, f, i))

# Process all files
for fileToSearch in files:
    try:
        for line in fileinput.input(fileToSearch, inplace=True):
            print(line.replace(textToSearch, textToReplace)),

    except Exception, e:
        print "Error replacing %s" % fileToSearch

# Copy icons
if isfile(srcIcon):
	print("Replace icons with %s" % srcIcon)
	destIcon = "munki/code/apps/Managed Software Center/Managed Software Center/Managed Software Center.icns"
	copyfile(srcIcon, destIcon)
	destIcon = "munki/code/apps/MunkiStatus/MunkiStatus/MunkiStatus.icns"
	copyfile(srcIcon, destIcon)

# Copy postflight script
if isfile(postinstall_script):
	print("Add postinstall script: %s" % postinstall_script)
	postinstall_dest = "munki/code/pkgtemplate/Scripts_app/postinstall"
	copyfile(postinstall_script, postinstall_dest)
	# Set execute bit
	st = stat(postinstall_dest)
	chmod(postinstall_dest, (st.st_mode | 0111))

print("Building Munki")
proc = subprocess.Popen(['./munki/code/tools/make_munki_mpkg.sh','-r','munki'])
proc.communicate()


