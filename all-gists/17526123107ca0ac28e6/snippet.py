#!/usr/bin/env python
import os
import zipfile

"""
Helper class that lets one add whole directory contents.

License
--------------------

The MIT License (MIT)

Copyright (c) 2014 Maciej "Nux" Jaros.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software 
and associated documentation files (the "Software"), to deal in the Software without restriction, 
including without limitation the rights to use, copy, modify, merge, publish, distribute, 
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is 
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or 
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING 
BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND 
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


Examples
--------------------

	# add whole "dir" to "test.zip" (when you open "test.zip" you will see only "dir")
	zip = ZipArchive('test.zip', 'w')
	zip.addDir('dir')
	zip.close()
	
	# add contents of "dir" to "test.zip" (when you open "test.zip" you will see only it's contents)
	zip = ZipArchive('test.zip', 'w')
	zip.addDir('dir', 'dir')
	zip.close()

	# add contents of "dir/subdir" to "test.zip" (when you open "test.zip" you will see only contents of "subdir")
	zip = ZipArchive('test.zip', 'w')
	zip.addDir('dir/subdir', 'dir/subdir')
	zip.close()

	# add whole "dir/subdir" to "test.zip" (when you open "test.zip" you will see only "subdir")
	zip = ZipArchive('test.zip', 'w')
	zip.addDir('dir/subdir', 'dir')
	zip.close()

	# add whole "dir/subdir" with full path to "test.zip" (when you open "test.zip" you will see only "dir" and inside it only "subdir")
	zip = ZipArchive('test.zip', 'w')
	zip.addDir('dir/subdir')
	zip.close()

	# add whole "dir" and "otherDir" (with full path) to "test.zip" (when you open "test.zip" you will see only "dir" and "otherDir")
	zip = ZipArchive('test.zip', 'w')
	zip.addDir('dir')
	zip.addDir('otherDir')
	zip.close()

	# add whole "dir" contents to "test.zip" to "foobar" (when you open "test.zip" you will see only "foobar" and inside it contents of "dir")
	zip = ZipArchive('test.zip', 'w')
	zip.addDir('dir', 'dir', inZipRoot='foobar')
	zip.close()
"""

class ZipArchive(zipfile.ZipFile):
	
	# If true then some info about added files/dirs is shown
	verbose = False
	
	# If true then some extra debug info will be shown
	showDebugInfo = False
	
	# not working: http://stackoverflow.com/questions/17106662/how-to-pass-all-arguments-from-init-to-super-class/17106700?noredirect=1#17106700
	def __init__(self, *args, **kwargs):
		"""
		Constructor with some extra params.
		
		@param verbose: be verbose about what we do. Defaults to True.
		
		For other params see: zipfile.ZipFile
		"""
		self.verbose = kwargs.pop('verbose', self.verbose)
		#super(ZipArchive, self).__init__(*args, **kwargs)
		zipfile.ZipFile.__init__(self, *args, **kwargs)
	
	def addEmptyDir(self, path, baseToRemove="", inZipRoot=None):
		"""
		Add empty dir under path to zip removing baseToRemove
		"""
		inZipPath = os.path.relpath(path, baseToRemove)
		if inZipPath == ".":	# path == baseToRemove (but still root might be added
			inZipPath = ""
		
		if inZipRoot!=None:
			inZipPath = os.path.join(inZipRoot, inZipPath)
		
		if inZipPath == "":		# nothing to add
			return

		if self.verbose:
			print "Adding dir entry: " + inZipPath
		zipInfo = zipfile.ZipInfo(os.path.join(inZipPath, ''))
		self.writestr(zipInfo, '')

	def addFile(self, filePath, baseToRemove="", inZipRoot=None):
		"""
		Add file under filePath to zip removing baseToRemove
		"""
		inZipPath = os.path.relpath(filePath, baseToRemove)
		
		if inZipRoot!=None:
			inZipPath = os.path.join(inZipRoot, inZipPath)
		
		if self.verbose:
			print "Adding file: " + filePath
			print "	Under path: " + inZipPath
		self.write(filePath, inZipPath)	
	
	def addDir(self, path, baseToRemove="", ignoreDirs=[".svn", ".git"], inZipRoot=None):
		"""
		Adding directory given by \a path to opened zip file \a self

		@param baseToRemove path that will be removed from \a path when adding to archive
		@param ignoreDirs directory names that are to be ignored
		"""

		#baseToRemove = baseToRemove.rstrip("\\/")
		ignoredRoots = []
		for root, dirs, files in os.walk(path):
			# ignore e.g. special folders
			dirName = os.path.basename(root)
			if ignoreDirs.count(dirName) > 0:
				ignoredRoots += [root]
				if self.showDebugInfo:
					print "ignored: " + root
				continue
			# ignore descendants of folders ignored above
			ignore = False
			for ignoredRoot in ignoredRoots:
				if root.startswith(ignoredRoot):
					ignore = True
					break
			if ignore:
				continue
			
			# add dir itself (needed for empty dirs)
			if len(files) <= 0:# and len(dirs) <= 0:	# NOT checking for dirs as entry for directory seem to be needed if it has no files (e.g. for Total Commander compare)
				if self.showDebugInfo:
					print "(root, baseToRemove, inZipRoot) = "
					print (root, baseToRemove, inZipRoot)
				self.addEmptyDir(root, baseToRemove, inZipRoot)
			
			# add files
			for file in files:
				self.addFile(os.path.join(root, file), baseToRemove, inZipRoot)

# test when run directly
if __name__ == '__main__':
	ZipArchive.verbose = True
	ZipArchive.showDebugInfo = False
	
	#"""
	from dir import *
	makeDirIfNotExist('test-dir/subdir')
	zip = ZipArchive('test.zip', 'w') #, verbose=False)
	zip.addDir('test-dir')
	zip.addDir('test-dir', inZipRoot='test2')
	zip.close()
	"""
	zip = ZipArchive('pliki_mini.zip', 'w', zipfile.ZIP_DEFLATED)	# ZIP_DEFLATED = compressed, ZIP_STORED is default
	zip.addDir('pliki_mini', 'pliki_mini', inZipRoot='pliki')
	zip.close()
	zip = ZipArchive('pliki_demo.zip', 'w', zipfile.ZIP_DEFLATED)
	zip.addDir('pliki_demo', 'pliki_demo', inZipRoot='pliki')
	zip.close()
	#"""
