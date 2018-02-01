#!python

import os, re

ld_list_file = 'ldconfig.list'
pattern = re.compile(r'.*=>\s*(?P<libfile>.*)\s*')
lib_files = map(lambda x: x.groupdict()['libfile'], 
				filter(lambda x: x, 
					map(lambda ln: pattern.match(ln), 
						file(ld_list_file, 'r'))))
for filepath in lib_files:
	try:
		fstat = os.stat(filepath)
		if (fstat.st_mode & 0o444) != 0o444:
			print '%o' % (fstat.st_mode & 0o777), filepath
	except OSError:
		print '[???]', filepath
