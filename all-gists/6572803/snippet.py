#!/usr/bin/python

import os, sys

def browse(n, dirname) :
	
	tab = "---" * n
	prevdir = os.getcwd() # storing current directory
	os.chdir(dirname) # migrating into the new directory

	for name in os.listdir(".") :
		if os.path.isfile(name) :
			print tab + name + " [file]"
		elif os.path.isdir(name) :
			print tab + name + " [directory] :"
			browse(n + 1, name) # directory found! time to hunt down more stuffs
	os.chdir(prevdir) # moving back to the previous directory

if len(sys.argv) == 2 :  # checks if argument is supplied
	if  os.path.isdir(sys.argv[1]) == False :
		print "Directory does not exist!"
		sys.exit()
	else :
		browse(1, sys.argv[1])
elif len(sys.argv) > 2 : # checks if more than 1 argument is supplied
	print "Please supply only one directory name"
	sys.exit()
else : # no arguments, so just browse the currect directory
	browse(1, ".")