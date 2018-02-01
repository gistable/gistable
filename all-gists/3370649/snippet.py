#!/usr/bin/python

# fix-xcode
# 	Rob Napier <robnapier@gmail.com>

# Script to link in all your old SDKs every time you upgrade Xcode
# Create a directory called /SDKs (or modify source_path).
# Under it, put all the platform directories:
# 	MacOSX.platform          iPhoneOS.platform        iPhoneSimulator.platform
# Under those, store the SDKs:
#	MacOSX10.4u.sdk MacOSX10.5.sdk  MacOSX10.6.sdk  MacOSX10.7.sdk  MacOSX10.8.sdk
#
# After upgrading Xcode, just run fix-xcode.

import argparse
import subprocess
import os

source_path = "/SDKs"

parser = argparse.ArgumentParser()
parser.add_argument('xcodePath', help='path to Xcode', nargs='?')
args = parser.parse_args()

if args.xcodePath:
	dest_path = args.xcodePath
else:
	dest_path = subprocess.check_output(["xcode-select", "--print-path"]).rstrip()

if not dest_path.endswith("/Contents/Developer"):
	dest_path += "/Contents/Developer"

for platform in os.listdir(source_path):
	subprocess.call("sudo ln -sf %(source_path)s/%(platform)s/* %(dest_path)s/Platforms/%(platform)s/Developer/SDKs" % locals(), shell=True)