#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""RAM disk creation (MacOS X only for now).

Usage:

with ramdisk(10240000, 'テスト1番') as x:
	print "Mountpoint is: %s" % x.path
	# use it
	print 'Closing...'
"""

import os
import pipes
import subprocess
import sys
import uuid
from contextlib import contextmanager


DEFAULT_SIZE = 1024000


if sys.platform != 'darwin':
	raise OSError('Only MacOS X supported for now')


import plistlib


class RamDisk(object):
	def __init__(self, size=DEFAULT_SIZE, name=None):
		if not name:
			name = 'ramdisk-%s' % uuid.uuid4().hex
		self.device = subprocess.check_output(
			['/usr/bin/hdiutil', 'attach' ,'-nomount' ,'ram://%i' % ((size + 511) / 512)]
		).strip()
		subprocess.check_output(
			['/usr/sbin/diskutil', 'erasevolume', 'hfsx', name, self.device]
		)
		self.path = plistlib.readPlistFromString(
			subprocess.check_output(
				['/usr/sbin/diskutil', 'info', '-plist', self.device]
			)
		)['MountPoint']

	def close(self):
		subprocess.check_output(
			['/usr/sbin/diskutil', 'eject', self.device]
		)


@contextmanager
def ramdisk(size=DEFAULT_SIZE, name=None):
	x = RamDisk(size, name)
	yield x
	x.close()
