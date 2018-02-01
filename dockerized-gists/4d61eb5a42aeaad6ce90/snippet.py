"""
Progress bar for rsync
========================

Shows file progress and total progress as a progress bar.

Usage
---------
Run rsync with -P and pipe into this program. Example::

	rsync -P -avz user@host:/onefolder otherfolder/ | python rsyncprogress.py

It will show something like this::

	65%|30652/117251|################         |ETA:  0:04:20|File:100%|Illustris-3/...68/gas2_subhalo_5885.hdf5|0:00:00|156.48kB/s
	
	                                                               ^ File progress 
	                                                                     ^ File name                             ^ ETA  ^ Speed
	                  ^ Overall progress bar   ^ and ETA
	           ^ total number of files
	       ^ files to be checked
	^ Overall progress

You need the progressbar package installed (see PyPI).

License
-----------
Copyright (c) 2015 Johannes Buchner

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import progressbar
import sys

def read_stdin():
	line = ''
	while sys.stdin:
		try:
			c = sys.stdin.read(1)
		except IOError as e:
			print e
			continue
		if c == '\r':
			# line is being updated
			yield line
			line = ''
		elif c == '\n':
			# line is done
			yield line
			line = ''
		elif c == '':
			break
		else:
			line += c

first_update = None
widgets = [progressbar.Percentage(), None, progressbar.Bar(), progressbar.ETA(), None]
pbar = None

for line in read_stdin():
	parts = line.split()
	if len(parts) == 6 and parts[1].endswith('%') and parts[-1].startswith('to-check='):
		# file progress -P
		file_progress = parts[1]
		file_speed = parts[2]
		file_eta = parts[3]
		istr, ntotalstr = parts[-1][len('to-check='):-1].split('/')
		ntotal = int(ntotalstr)
		i = int(istr)
		j = ntotal - i
		total_progress = j * 100. / int(ntotal)
		widgets[1] = '|%s/%s' % (i, ntotal)
		widgets[-1] = '|File:%s|%s|%s|%s' % (file_progress, short_file_name, file_eta, file_speed.rjust(10))
		if pbar is None:
			first_update = j
			pbar = progressbar.ProgressBar(widgets=widgets,
				maxval=ntotal - first_update).start()
		pbar.maxval = ntotal - first_update
		pbar.update(j - first_update)
		
		#sys.stderr.write('Total:%.1f%%|File:%s|%s|%s|%s|\r' % (total_progress, file_progress,
		#	short_file_name, file_eta, file_speed))
		#sys.stderr.flush()
	elif not line.startswith(' '):
		# total progress
		file_name = line
		if len(parts) == 6: print parts[1].endswith('%'), parts[-1].startswith('to-check='),
		if len(file_name) > 40:
			short_file_name = file_name[:12] + '...' + file_name[-(28-3):]
		else:
			short_file_name = file_name
pbar.finish()
