#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2012-2015 Hydriz Scholz
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import boto
from boto.s3.connection import OrdinaryCallingFormat
from filechunkio import FileChunkIO
import math
import os
import settings
import sys

class DumpsMultipart:
	def __init__( self ):
		self.accesskey = settings.accesskey
		self.secretkey = settings.secretkey
		self.conn = boto.connect_s3( self.accesskey, self.secretkey, host='s3.us.archive.org', is_secure=False, calling_format=OrdinaryCallingFormat() )

	def upload( self, dumpfile, identifier ):
		item = self.conn.get_bucket( identifier )
		filesize = os.stat( dumpfile ).st_size
		header = {
			'x-archive-queue-derive': '0'
		}
		# Initiate the multipart upload request
		mp = item.initiate_multipart_upload( os.path.basename( dumpfile ), headers=header )

		# Use a chunk size of 200 MB
		chunksize = 209715200
		chunkcount = int( math.ceil( filesize / chunksize ) )

		# Send the file parts, using FileChunkIO to create a file-like object
		# that points to a certain byte range within the original file. We
		# set bytes to never exceed the original file size.
		for i in range( chunkcount + 1 ):
			offset = chunksize * i
			bytes = min( chunksize, filesize - offset )
			with FileChunkIO( dumpfile, 'r', offset=offset, bytes=bytes ) as fp:
				mp.upload_part_from_file( fp, part_num=i + 1, headers=header )

		# Complete the multipart upload
		mp.complete_upload()

	def process( self ):
		self.upload( sys.argv[1], sys.argv[2] )

if __name__ == "__main__":
	DumpsMultipart = DumpsMultipart()
	DumpsMultipart.process()
