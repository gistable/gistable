# extract_iphone_backup.py version 0.01
# Adam Geitgey <ageitgey@gmail.com>
#
# Feel free to use this code however you see fit.  However, this file deals with
# backup files directly.  Please be careful!
#
# This software is provided 'as-is', without any express or implied warranty. In
# no event will the author be held liable for any damages arising from the use
# of this software.
#
# Purpose:
# This script will extract all the files from all iPhone backups in the current
# user's home folder.
#
# Usage: python extract_iphone_backup.py
#
# Output: iphone_backup/your_phone_number/*
#  where * is all the files contained in the backup.
#

import glob
import os
import os.path
import plistlib

#Given an iPhone backup folder, this will get it's phone number
def getIPhoneNumber(path):
		pl = plistlib.readPlist(path+"/Info.plist")
		return pl['Phone Number']

#Make a folder to hold the output files
try:
	os.mkdir("iphone_backup")
except:
	pass
	
#each iPhone backup is in a seperate folder
for backupPath in glob.glob(os.path.expanduser("~/Library/Application Support/MobileSync/Backup/*")):
	phoneNum = getIPhoneNumber(backupPath)

	#Make a folder for this iPhone
	try:
		os.mkdir("iphone_backup" + os.path.sep + phoneNum)
	except:
		pass

	#each backup folder contains a bunch of *.mdbackup files that are really
	#binary plist files that have a Data node that contains the backed-up file
	for path in glob.glob(backupPath + os.path.sep + "*.mdbackup"):

		#use plutil to turn the bplist into a plist
		os.system("plutil -convert xml1 -o /tmp/temp.pl \"%s\"" % path)
		pl = plistlib.readPlist("/tmp/temp.pl")

		#The Path key stores the original file name
		#We can use that to recreate the backed-up files
		originalBackupFileName = pl['Path']
		outputFile = "iphone_backup" + os.path.sep + phoneNum + os.path.sep + originalBackupFileName.replace("/", "_")

		#Some of the backed-up files are bplists themselves.  For convenience,
		#lets go ahead and make those human-readable
		if pl['Data'].data[0:6] == "bplist":
			#write out the bplist file!
			outputFileHandle = open("/tmp/temp2.pl", "w")
			outputFileHandle.write(pl['Data'].data)
			outputFileHandle.close()

			#use plutil to turn the bplist into a plist
			os.system("plutil -convert xml1 -o \"%s\" /tmp/temp2.pl" % outputFile)
			
			print outputFile + " - converted and extracted"

		#But other files (sqlite databases, etc) don't need further processing
		else:
			#write out the actual backed-up file
			outputFileHandle = open(outputFile, "w")
			outputFileHandle.write(pl['Data'].data)
			outputFileHandle.close()
			
			print outputFile + " - extracted"
