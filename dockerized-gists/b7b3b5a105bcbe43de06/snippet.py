#! /usr/bin/python

import sys
import os


def main():
	if len(sys.argv) < 2:
		print "Usage: profile.py <path> | <UUID>"
		sys.exit()

	arg = sys.argv[1]

	if "." in arg:
		handle_path(arg)

	else:
		handle_uuid(arg)


def handle_path(path):
	command = "security cms -D -i '%s'" % (path)
	os.system(command)

def handle_uuid(arg):
	profiles_dir = os.path.expanduser("~/Library/MobileDevice/Provisioning Profiles/")
	profiles = os.listdir(profiles_dir)

	correct_paths = [x for x in profiles if x.startswith(arg)]
	if len(correct_paths) == 0:
		print "Profile with UUID [%s] not found" % arg
		sys.exit()

	path = correct_paths[0]

	profile_path = os.path.join(profiles_dir, path)
	handle_path(profile_path)


if __name__ == "__main__":
	main()