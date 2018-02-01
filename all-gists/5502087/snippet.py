#!/usr/bin/env python
#
#require: https://github.com/richardasaurus/mega.py
#
import os
import sys
from mega import Mega

mega = Mega({'verbose': True})
m = mega.login('megauseremail', 'megapass')

curDir = os.getcwd() + os.path.sep
dstDirId = None

if len(sys.argv)>1 and sys.argv[1]:
	srcs = sys.argv[1:]
else:
	srcs = None

print srcs

if srcs:
	if len(srcs) > 1 and not os.path.isfile( srcs[-1] ):#if last param isn't a local file then it is dest remote folder
		dstName = srcs.pop()
		dstId = m.find( dstName )
		if dstId:
			dstDirId = dstId[0]
			print 'Destination Folder: '+ dstName

	for src in srcs:
		srcFile = curDir + src
		if os.path.isfile( srcFile ):
			#print srcFile
			#print dstDirId
			uppedFile = m.upload(srcFile, dstDirId)
			print uppedFile
			print 'Upped File Link: ' + m.get_upload_link( uppedFile )
