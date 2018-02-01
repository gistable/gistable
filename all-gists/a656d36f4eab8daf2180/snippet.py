#!/usr/bin/env python

# installAPK.py
# Author; George Lester
# Created; 2016-01

# Uninstalls (and reinstalls) the given APK by path.
# This is needed in some cases where:
#   - signed/unsigned APKs conflict, 
#   - `adb install -r` does not actually do anything, 
#   - and when using `-r` fails to freshly install new APKs (fails if they are not present in the first place)

import distutils.spawn
import sys
import subprocess
import os
import re

ADB_NAME = "adb"
AAPT_NAME = "aapt"

def main():
	
	apkPath, apkName = determineAPKName()
	
	if(apkName == None or apkPath == None):
		print("Unable to determine APK details from first positional parameter (should be a path to an APK file)")
		return 1
	
	if(not checkADB()):
		print("Unable to find 'adb' and 'aapt' tools in PATH (is the android SDK installed?)")
		return 1
	
	if(not uninstallAPK(apkName)):
		print("Unable to uninstall APK")
		return 1
	
	if(not installAPK(apkPath)):
		print("Unable to install APK")
		return 1
	
	return 0
	
# Returns a tuple representing the absolute path of the file from the first positional argument, and the package name.
# If there are not enough positional arguments, the tuple returned contains two Nones.
def determineAPKName():
	
	if(len(sys.argv) != 2):
		return (None, None)
	
	apkPath = os.path.abspath(sys.argv[1])
	
	packageDiscoveryCommand = [AAPT_NAME, "dump", "badging", apkPath]
	output = subprocess.check_output(packageDiscoveryCommand)
	
	if(output == None):
		return (None, None)
	
	# find the package.
	packageRegex = re.compile("package: name='([a-zA-Z0-9._]+)'")
	matches = re.findall(packageRegex, output)
	if(matches == None or len(matches) <= 0):
		return (None, None)
	
	return (apkPath, matches[0])

# Removes the given [apkName], returns false if the APK is not uninstalled after this returns.
def uninstallAPK(apkName):
	
	print("Uninstalling any extant APKs...")
	
	uninstallCommand = [ADB_NAME, "uninstall", apkName]
	result = subprocess.check_output(uninstallCommand)
	
	if("DELETE_FAILED_INTERNAL_ERROR" in result):
		return True
	if(len(result) <= 0 or "Success" in result):
		return True
	
	print(result)
	return False
	
# Installs the APK located at the given [apkPath], returns True if the install was successful, False otherwise.
def installAPK(apkPath):
	
	print("Installing APK...")
	
	installCommand = [ADB_NAME, "install", apkPath]
	return subprocess.call(installCommand) == 0
	
# Returns true if ADB and AAPT is in the PATH, false otherwise.
def checkADB():
	
	if(distutils.spawn.find_executable(ADB_NAME) == None):
		return False
	if(distutils.spawn.find_executable(AAPT_NAME) == None):
		return False
	return True
	
status = main()
if(status != 0):
	sys.exit(status)