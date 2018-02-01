#!/usr/bin/env python
# 
#  clearsvnentries.py
#  scripts
#  
#  Created by Dirk on 2009-06-03.
#  Copyright 2009 Sofa BV. Use for good, not bad.
# 

import os
import sys
import shutil

def clearpath(targetPath, silent=False):
	currentWorkingDirectory = os.getcwd()
	os.chdir(targetPath)
	
	found = 0
	for directoryPath, directoryNames, fileNames in os.walk('.'):
		for directoryName in directoryNames:
			if directoryName == u'.svn':
				path = os.path.abspath(os.path.join(directoryPath, directoryName))
				if os.path.isdir(path):
					found += 1
					if not silent:
						print u'Removing \'%s\'' % (path)
					shutil.rmtree(path)
	os.chdir(currentWorkingDirectory)
	if not silent:
		if not found:
			print 'No .svn metadata found in \'%s\'.' % (os.path.abspath(targetPath))
		else:
			print 'Deleted %i .svn folder%s in \'%s\'.' % (found, ([c for c in 's' if found>1] or [''])[0], os.path.abspath(targetPath))

if __name__ == '__main__':
	if len(sys.argv) >= 2:
		targetPath = sys.argv[len(sys.argv)-1]
		silent = u'-s' in sys.argv or u'--silent' in sys.argv
		clearpath(targetPath, silent=silent)
	else:
		fileName = os.path.split(__file__)[1]
		print 'Clears .svn metadate from directories recursively.\nUsage: %s <path>\noption: -s or --silent to print no output' % (fileName)
		sys.exit()
