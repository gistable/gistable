#! /usr/bin/env python3
#
# Handles producing symbolic links to various library folders, for different
# texture compression options in Unity Android, or to switch libraries for
# different platforms
#
# Unity stores all its imported data inside its ./Library/ folder, containing
# only derived data for your project. When switching platforms or texture 
# compression settings, contents of this folder change accordingly, but can
# be preserved between switches. This script can help needlessly importing
# assets when platform switches happen regularly, without needing to rely
# on keeping multiple asset copies or running a Unity Cache Server.
#
# WARNING: This script will alter your files. Use at your own risk.
# Especially when performing initial folder preparation, be sure to back up 
# your files in case something goes wrong. Once it's done, your Unity project 
# will have its root in a new, different directory, so paths to source control
# and in Unity itself will need to be updated.
#
# Requires Python >= 3.2
#
# Usage examples
# ./switchLibrary.py Standalone
# ./switchLibrary.py AndroidATC
# ./switchLibrary.py --prepare iOS
#
# Expects project folder arrangement:
# ./Libraries/
# ./Libraries/<LIBRARY1>
# ./Libraries/<LIBRARY2>
# ./Libraries/<LIBRARY...>
# ./Project/
# ./Project/<UNITY-PROJECT-FILES...>
# ./switchLibrary.py
#
# Can transform existing projects into this format. Place inside root Unity
# folder and execute with --prepare.
# --prepare can take an optional parameter that determines the name of the
# existing library when symlinks are created.
#
# WINDOWS NOTE:
# On MS Windows, permissions to create symbolic links are not granted
# by default to ordinary users. As a result, the script needs to be
# executed with administrator privileges

import os
import os.path
import sys
from argparse import ArgumentParser

TempPath = os.path.join("Project", "Temp", "UnityLockfile")

# Safety checks
# Look for temp folder first of all. If it exists, we assume Unity is running
if (os.path.exists(TempPath)):
	print("Unity seems to be running (Lock file exists).\nClose Unity first.")
	sys.exit(-1)

# Create argument parser
parses = ArgumentParser(description='Unity library switcher')
group = parses.add_mutually_exclusive_group(required=True)
group.add_argument('library', nargs='?',
	help='The name of the library to switch to. This should be a valid directory under ./Library/')
group.add_argument('--prepare', const='library', nargs='?',
	help="Prepare an existing Unity library for symlinking. Can be provided with an optional parameter that determines the current library's name")
args = parses.parse_args();

# Switch library?
if args.library != None:
	LibraryPath = os.path.join("Project", "Library")

	# Check if the existing library folder is a symbolic link. If not, we stop too
	if (not os.path.islink(LibraryPath) and os.path.exists(LibraryPath)):
		print("Library directory is not a symbolic link.\nNot continuing in case we destroy data.\n\nDo you need to prepare your Unity folder first?")
		sys.exit(-2)

	newLibrary = sys.argv[1]
	newLibraryPath = os.path.join("Libraries", newLibrary)

	# Check if the new library folder exists
	if (not os.path.exists(newLibraryPath)):
		print ("Library directory {} does not appear to exist.\nDoing nothing.\n\nDo you need to prepare your Unity folder first?".format(newLibrary))
		sys.exit(-3)

	# Do the stuff!
	# Remove existing symlink
	if (os.path.exists(LibraryPath)):
		os.remove(LibraryPath)
	# Create folder symlink
	os.symlink(os.path.join("..", newLibraryPath), LibraryPath, True)

elif args.prepare != None:
	# Transform existing Unity library.
	TempPath = os.path.join("Temp", "UnityLockfile")
	SymlinkLibraryPath = os.path.join("Libraries")
	ProjectPath = os.path.join("Project")

	# Look for temp folder in different root path, because we're expected to run in a different folder structure
	if (os.path.exists(TempPath)):
		print("Unity seems to be running (Lock file exists).\nClose Unity first.")
		sys.exit(-1)

	# Check if the existing library folder is a symbolic link. If it is, we don't know what to do
	if (os.path.islink(os.path.join("Library"))):
		print("Library directory is already a symbolic link.\nNot continuing in case we destroy data.")
		sys.exit(-2)

	# Check if the existing library folder is a symbolic link. If it is, we don't know what to do
	if (os.path.exists(ProjectPath)):
		print("A Project directory already exists in this Unity folder.\nNot continuing in case we stomp something.")
		sys.exit(-4)

		# Check if the existing library folder is a symbolic link. If it is, we don't know what to do
	if (os.path.exists(SymlinkLibraryPath)):
		print("A Libraries directory already exists in this Unity folder.\nNot continuing in case we stomp something.")
		sys.exit(-5)

	# Get file list BEFORE we make new folders
	allFiles = os.listdir()

	os.mkdir(ProjectPath)
	os.mkdir(SymlinkLibraryPath)

	# Loop through all files in CWD
	for existingFile in allFiles:
		newPath = os.path.join(ProjectPath, existingFile)

		if existingFile == os.path.basename(__file__): # found ourselves!
			print("Found ourselves. We stay put")
		elif os.path.isdir(existingFile):
			if existingFile == "Library":
				newPath = os.path.join(SymlinkLibraryPath, args.prepare)

				print("Found library dir {}. Moving to {}".format(existingFile, newPath))

				os.rename(existingFile, newPath)

				symlinkPath = os.path.join(ProjectPath, "Library")
				relativePath = os.path.join("..", newPath)

				print("Creating symlink to {} at {}".format(relativePath, symlinkPath))
				os.symlink(relativePath, symlinkPath, True)
			else:
				print("Found dir {}. Moving to {}".format(existingFile, newPath))

				os.rename(existingFile, newPath)
		else:
			print("Found file {}. Moving to {}".format(existingFile, newPath))

			os.rename(existingFile, newPath)