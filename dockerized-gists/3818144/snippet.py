import os
import sys

argument = sys.argv[1]

install = False

if argument.endswith(".apk"):
	install = True

revision = os.popen("adb devices").read()
devices = revision.split("\n")

for device in devices:
	if device.endswith("device"):
		deviceId = device.split("\t")[0]
		print "\"" + deviceId + "\""
		if install:
			print os.popen("adb -s " + deviceId + " install -r " + argument).read()
		else:
			print os.popen("adb -s " + deviceId + " uninstall " + argument).read()
		
		