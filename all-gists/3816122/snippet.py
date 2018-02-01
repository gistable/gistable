#!/usr/bin/python

import zipfile
import glob
import fnmatch
import sys
import json
import os

import Foundation
import envoy # easy_install -U envoy

# you also need ideviceinstaller: brew install ideviceinstaller

# Plug in all your devices, unlock them and then run this script, this script
# will tell you what apps you have in itunes that are not installed on your 
# devices. You're probably going to want to sync iTunes with your devices before
# running this.
#
# You can then use this information to purge itunes of these junk apps.
#
# This script creates files on your desktop called iTunes.json and <UDID>.json -
# you'll want to trash them when done.

class AppInventory(object):

	def __init__(self, name):
		self.name = name
		self.apps = dict()

	def read_from_iTunes(self):
		if os.path.exists(os.path.expanduser('~/Desktop/%s.json' % self.name)):
			self.apps = json.load(file(os.path.expanduser('~/Desktop/%s.json' % self.name)))
		else:
			path = os.path.expanduser('~/Music/iTunes/iTunes Music/Mobile Applications/*.ipa')
			for thePath in glob.glob(path):
				theZipfile = zipfile.ZipFile(thePath, 'r')
				theNames = theZipfile.namelist()
				
				for theName in theNames:
					if fnmatch.fnmatch(theName, 'Payload/*.app/Info.plist'):
						theData = theZipfile.read(theName)
						theData = Foundation.NSData.dataWithBytes_length_(theData, len(theData))
						thePropertyList, theMutablilityOption, theError = Foundation.NSPropertyListSerialization.propertyListFromData_mutabilityOption_format_errorDescription_(theData, Foundation.NSPropertyListImmutable, None, None)
						self.process_infoplist(theName, thePropertyList)

	def read_from_device(self, udid):
		if os.path.exists(os.path.expanduser('~/Desktop/%s.json' % self.name)):
			self.apps = json.load(file(os.path.expanduser('~/Desktop/%s.json' % self.name)))
		else:
			r = envoy.run('ideviceinstaller -l -o xml --uuid %s' % udid)
			theData = Foundation.NSData.dataWithBytes_length_(r.std_out, len(r.std_out))
			thePropertyList, theMutablilityOption, theError = Foundation.NSPropertyListSerialization.propertyListFromData_mutabilityOption_format_errorDescription_(theData, Foundation.NSPropertyListImmutable, None, None)
			for theInfoPlist in thePropertyList:
				self.process_infoplist(None, theInfoPlist)

	def process_infoplist(self, name, plist):
		theBundleName = None
		if 'CFBundleName' in plist:
			theBundleName = plist['CFBundleName']
		theVersion = None
		if 'CFBundleVersion' in plist:
			theVersion = plist['CFBundleVersion']
		theIdentifier = None
		if 'CFBundleIdentifier' in plist:
			theIdentifier = plist['CFBundleIdentifier']
		if not theIdentifier:
			print '# Info.plist with no identifier'
			print plist
			sys.exit(0)
			return
		if not theBundleName or not theVersion:
			print '# Corrupt file', theIdentifier
			return
		if theIdentifier in self.apps:
			print '# Duplicate'
			return
		self.apps[theIdentifier] = (theBundleName, theIdentifier, theVersion)

	def save(self):
		json.dump(self.apps, file(os.path.expanduser('~/Desktop/%s.json' % self.name), 'w'), indent=4)

itunes = AppInventory('itunes')
itunes.read_from_iTunes()
itunes.save()

theDeviceInventories = []

r = envoy.run('idevice_id -l')
theUDIDs = [theUDID for theUDID in r.std_out.split('\n') if theUDID]
for theUDID in theUDIDs:
	print '# Scanning', theUDID
	theDeviceInventory = AppInventory(theUDID)
	theDeviceInventory.read_from_device(theUDID)
	theDeviceInventory.save()
	theDeviceInventories.append(theDeviceInventory)

for theApp in itunes.apps:
	found = False
	for theDeviceInventory in theDeviceInventories:
		if theApp in theDeviceInventory.apps:
			found = True
			break
	if not found:
		print itunes.apps[theApp]