# update_timezones.py
# Aleksandr Pasechnik
#
# Goes through the Day One jounal and sets the Time Zone of each entry that
# doesn't already have one to the value of the *timezone* variable. Makes a
# backup copy of each entry it modified by adding a '.tzbak' to the filename.
# Ignores any entry that already has a '.tzbak' version.
# 
# NOTE: base_dir may need to be adjusted to the correct Journal_dayone location
# NOTE: It is probably a good idea to have a full journal backup just in case
# something goes wrong

import os
import plistlib
import shutil

timezone = 'America/New_York'
base_dir = '~/Library/Mobile Documents/5U8NS4GX82~com~dayoneapp~dayone/Documents/Journal_dayone/'

base_dir = os.path.expanduser(base_dir)
entries_dir = os.path.join(base_dir,'entries')

files = os.listdir(entries_dir)
files[:] = [file for file in files if file.endswith('.doentry')]

for file in files:
	filename = os.path.join(entries_dir,file)
	entry = plistlib.readPlist(filename)
	if 'Time Zone' not in entry.keys():
		print 'Found an entry without a time zone:', entry['UUID']
		entry['Time Zone'] = timezone
		backupfilename = filename+'.tzbak'
		if not os.path.exists(backupfilename):
			print '	Backing up %s to %s'%(filename,backupfilename)
			shutil.move(filename,backupfilename)
			print '	Writing new entry at %s'%(filename)
			plistlib.writePlist(entry,filename)
		else:
			print '	Not doing anything because backup already exists at %s'%backupfilename
		print ''

print 'Done.'

