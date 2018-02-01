#!/usr/bin/python
## License: CC0
## Author: Marco Goetze
## Web: http://solariz.de
## Version: 1.2
## DIZ:
## Little Helper Script for Linux to make my KeePass Copy and Paste cooperate again with
## Chrome Browser.
## You need to have the latest keepass version and XSEL installed.
## Tested with:
## 	xsel 1.2.0
##  keepass 2.27
##  xdpyinfo 1.3.1
##  chrome 36
##  on Linux Mint Qiana (x64) on MATE and Cinnamon but should work on any gnome based desktop
##
## Plese see this chrome topic for discussion: https://productforums.google.com/forum/#!topic/chrome/4s5_Sx-e4z0
##


## You can edit this if needed, I use it since v1.2 to prevent the clipboard copy operation on each Copy Action
## it should only run when invoked by LastPass. To make this happen be sure you have 'xdotool' & 'xsel' installed
## apt-get install xdotool xsel
## without this script will not work!
##
window_name_matches = ['KeePass', 'kdbx', 'Edit Entry', 'Add Entry']

## no need for changes below here
from gi.repository import Gtk, Gdk
import subprocess

glob_inhalt = ""
print "KeePass Linux Clipboard Workaround"
print "Version 1.2 by Marco Goetze (www.solariz.de)"

def test(*args):
	global glob_inhalt
	found = False
	# Get Clipboard
	task = subprocess.Popen("xsel -o -b", shell=True, stdout=subprocess.PIPE)
	data = task.stdout.read()
	assert task.wait() == 0
	# check if changed
	if data != glob_inhalt:
		glob_inhalt = data
		print "Clipboard changed, checking if Lastpass Window is active..."
		task = subprocess.Popen("xdotool getactivewindow getwindowname", shell=True, stdout=subprocess.PIPE)
		winID = task.stdout.read().rstrip('\n')
		## print winID
		for s in window_name_matches:
			if s in winID:
				found = True

		if found == True:
			print "Match detected, processing Clipboard..."
			# wtf... yes, this works. From Clipboard to Primaty to clipboard and chome have it in CTRL-V
			task = subprocess.Popen("xsel -o -b|xsel -i -p;xsel -o -p|xsel -i -b", shell=True, stdout=subprocess.PIPE)
			data = task.stdout.read()
			assert task.wait() == 0
		else:
			print "No Match."

clip = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
clip.connect('owner-change',test)
Gtk.main()
