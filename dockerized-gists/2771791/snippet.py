#!/usr/bin/python

import sys
import argparse
import os
import re

'''
A simple script to create lower-resolution Android drawables from higher-resolution ones.

For example, given a batch of -xhdpi images, you can generate -hdpi and -mdpi images.

This makes it possible to only export highest-resolution artwork from image authoring tools, and
automate the rest.

Usage:

   drawable_convert.py -d res/drawable-mdpi -d res/drawable-hdpi res/drawable-xhdpi-v14/select*.png
   
   ... will take select*.png from xhdpi and place versions into mdpi and hdpi folders.
   
   Correct resize ratios are computed based on resource directory names.
   
   Actual scaling is done by ImageMagick's convert command.
'''

class Converter:
	def __init__(self, dstList):
		print u'Dst list: {0}'.format(dstList)
		self.mDstList = dstList
		
	def convert(self, src):
		for dstpath in self.mDstList:
			(srcpath, srcname) = os.path.split(src)
			dst = os.path.join(dstpath, srcname)
			self.convertOne(src, dst)

	def convertOne(self, src, dst):
		print u'\n*****\n{0} to {1}\n*****\n'.format(src, dst)
		'''
		Determine relative density
		'''
		srcDpi = self.getDpi(src)
		dstDpi = self.getDpi(dst)
		
		if srcDpi < dstDpi:
			print u'NOT converting from {0}dpi to {1}dpi'.format(srcDpi, dstDpi)
		else:
			factor = dstDpi*100/srcDpi
			print u'Converting from {0}dpi to {1}dpi, {2}%'.format(srcDpi, dstDpi, factor)
			cmd = u'convert -verbose "{0}" -resize "{2}%x{2}%" "{1}"'.format(src, dst, factor)
			os.system(cmd)
		
	def getDpi(self, f):
		p = os.path.dirname(f)
		if re.match('.*drawable.*\\-mdpi.*', p):
			return 160
		elif re.match('.*drawable.*\\-hdpi.*', p):
			return 240
		elif re.match('.*drawable.*\\-xhdpi.*', p):
			return 320
		else:
			raise ValueError(u'Cannot determine densitiy for {0}'.format(p))

if __name__ == "__main__":
	'''
	Parse command line arguments
	'''
	parser = argparse.ArgumentParser(description='Converts drawable resources in Android applications')
	parser.add_argument('-d', dest='DST', action='append', required=True, help='destination directory')
	parser.add_argument('src', nargs='+', help='files to convert (one or more)')
	args = parser.parse_args()

	cv = Converter(args.DST)
	for src in args.src:
		cv.convert(src)


'''


if [ $# -lt 1 ] ; then
	echo "Usage: $0 file_list"
	exit 1
fi

for f in $*
do
	echo "File: ${f}"
	convert -verbose "${f}" -resize "75%x75%" "../drawable-hdpi/${f}"
	convert -verbose "${f}" -resize "50%x50%" "../drawable-mdpi/${f}"
done

'''
