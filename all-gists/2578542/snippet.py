# File: mp3_tag.py
#
# Description: This module provides MP3 tags correction, i.e. from 
# 			any encoding X to UTF-8, the standard across different apps
# 			and platforms. The default parameters target the common Chinese 
#			encoding GBK.
#
# Features: 1. it recursively handles MP3 files > 512KB in all subdirectories.
#			2. outputs a log formatted to show the directory structure
#			with failures (decoding/encoding error, the field will be
#			kept in its original state).
#			3. decodes the tags character by character and preserves
#			UTF-8 characters (some tags mixed characters in UTF-8 and
#			other encodings). This also makes it safe to run this program
#			multiple times over the same files (it won't change the 
#			previously converted content.			
#
# Requirement: This used mutagen library. 
#
# Note: mutagen saves all output tags in ID3v2.4 which is not supported
# 		by win 7 file explorer or windows media player(they support up to 
#		ID3v2.3). So if you want to see the tags in win 7 explorer, you
#		need to convert them with other tools, such as iTunes.
#
# Use: at your command prompt, type:
#			python mp3_tag.py [<dir>]
# 		where the optional <dir> is the directory of MP3 files (handles the
#		current directory if missing)
#
# More info: http://blog.falcondai.com/2012/05/text-encoding-conversion.html
#
# Author: Falcon Dai
#
# Date: 4/26/2012
#
# License: Regarding the utility code, I do not provide any warranty but
# 		you are free to do whatever with these code. It edits some tags of 
#		your MP3 files, specifically only the album, artist, album artist, 
#		performer, and genre fields (you can modify this) so you might 
#		wanna test it on a few duplicates before running it on your entire 
#		music library.

from __future__ import unicode_literals
import os
from mutagen.easyid3 import EasyID3

def decode_mixed(entry, encoding):
	"""
	decode a (mixed) string character by character.
	@param: entry - a string that might contain text
					in mixed encoding (raw code point
					and encoding)
			encoding - the encoding used in the entry
	@return: a unicode string decoded from the entry
	"""
	t = u''
	s = bytearray()
	
	for i in range(len(entry)):
		c = entry[i]
		rc = c.encode('raw_unicode_escape')

		if len(rc) == 6:
			# byte is a code point (len = 6)
			t += s.decode(encoding)
			t += c
			s = bytearray()
		else:
			# raw byte
			s += rc

		if i == len(entry)-1:
			# at the end of entry
			t += s.decode(encoding)
	return t

def main(path):
	print 'working on %s and all its subdirectories...' % path
	log = open('mp3_tag_change.log', 'w')
	
	# change encoding to your guess of the encoding, for supported
	# encodings, check http://docs.python.org/library/codecs.html#standard-encodings
	# GBK is a good guess for Chinese songs
	encoding = 'gbk'
	error_count = fix(path, log, 0, encoding)
	
	print 'SUMMARY'
	print 'encountered %d errors.' % error_count
	log.write('encountered %d errors.' % error_count)
	log.close()
	
def fix(dir, log, nt, encoding):
	"""
	recursively fixes the mp3 tags in the designated directory with 
	a guess encoding. Note that the mp3 tags will be saved in ID3v2.4 format.
	@param: dir - the directory that contains the mp3 files to be fixed
			log - the log file to dump the logging information
			nt - the numbers of tabs to start with for nice logging
	@return: number of errors encountered (counted by fields) 
	"""
	print dir.encode('raw_unicode_escape')
	
	# change to the desired directory
	os.chdir(dir)
	
	for i in range(nt):
		log.write('\t')
	log.write(dir.encode('utf8'))
	log.write('\\\n')
	log.flush()
	
	# scan for mp3 files
	fl = os.listdir('.')
	dirs = []
	fs = []
	for f in fl:
		if os.path.isdir(f):
			# found a directory
			dirs.append(f)
		# change the size criterion to convert smaller MP3's
		if f.split('.')[-1] == 'mp3' and os.stat(f).st_size > 512 * 1024:
			# found an mp3 files larger than 512kb
			fs.append(f)

	# handle each file with tags in the following fields
	# change this list to convert more or less fields
	fields = ['album', 'artist', 'title', 'album artist', 'performer', 'genre']
	
	n = 0
	ne = 0
	for f in fs:
		print f.encode('raw_unicode_escape')
		
		# log the file name with prefixing tabs
		for i in range(nt+1):
			log.write('\t')
		log.write(f.encode('utf8'))
		
		try:
			# read and rewrite tags
			tags = EasyID3(f)
		
			for field in fields:
				if tags.has_key(field):
					new_tag = []
					try:
						for entry in tags[field]:
							if entry != '':
								t = decode_mixed(entry, encoding)
								new_tag.append(t)
						tags[field] = new_tag
					except:
						print 'encountered an error in '+field
						log.write(' encountered an error in '+field)
						ne += 1
			tags.save()
		
		except:
			# this program only handles IDv3 tags as it is
			# written now. But you can do more with mutagen
			log.write(' not in IDv3 format')
			ne += 1
		
		log.write('\n')
		log.flush()
		n += 1
	print 'edited %d mp3 files.' % n
	
	for dir in dirs:
		# update the error counts
		ne += fix(dir, log, nt+1, encoding)
		
	os.chdir('..')
	
	return ne
	
if __name__ == '__main__':
	import sys
	if len(sys.argv) < 2:
		main('.')
	else:
		main(sys.argv[1])