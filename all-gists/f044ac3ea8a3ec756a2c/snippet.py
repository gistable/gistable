#!/usr/bin/env python

import os
import sys
import shutil
import subprocess

if len(sys.argv) < 3:
	sys.exit("Usage: python sign.py <identity> <myApp.app>")

SCRIPT, IDENTITY, APP_PATH = sys.argv

def run(command):
	return subprocess.check_output(command, shell=True)

def listIdentities():
	run("certtool y | grep Developer\ ID")
	run("security find-identity")

def sign(path):
	run("codesign --verbose --force --sign '%s' '%s'" % (IDENTITY, path))

def signDir(path):

	if not os.path.exists(path):
		return

	for name in os.listdir(path):
		sign(os.path.join(path, name))

def signCheck(path):
	run("codesign --verify --verbose=100 '%s'" % (path))
	run("spctl -vvvvvv --assess --type execute '%s'" % (path))

applicationPath = os.path.abspath(APP_PATH)
signedApplicationPath = applicationPath

# Extract specific paths from the application
signedApplicationFrameworksPath = os.path.join(signedApplicationPath, "Contents", "Frameworks")
signedApplicationLibrariesPath = os.path.join(signedApplicationPath, "Contents", "Libraries")

# Sign all the frameworks
signDir(signedApplicationFrameworksPath)

# Sign all the libraries
signDir(signedApplicationLibrariesPath)

# Sign the application bundle
sign(signedApplicationPath)

signCheck(signedApplicationPath)
