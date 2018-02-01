#!/usr/bin/python
#
#  Read a CSV/TSV with a header row (!) and put it into a new sqlite table

import sys
import csv
import sqlite3


class Importer (object):
	_sqlite = None
	filepath = None
	
	def __init__(self, csv_path):
		self.filepath = csv_path
	
	def sqlite_handle(self, dbpath):
		if self._sqlite is None:
			self._sqlite = sqlite3.connect(dbpath)
		return self._sqlite
	
	def import_to(self, dbpath, csv_format='excel-tab'):
		assert self.filepath
		assert dbpath
		
		# SQLite handling
		sql_handle = self.sqlite_handle(dbpath)
		sql_handle.isolation_level = 'EXCLUSIVE'
		sql_cursor = sql_handle.cursor()
		create_sql = 'CREATE TABLE rows '
		insert_sql = 'INSERT INTO rows '
		
		# loop rows
		with open(self.filepath, 'rb') as csv_handle:
			reader = unicode_csv_reader(csv_handle, dialect=csv_format)
			try:
				i = 0
				for row in reader:
					sql = insert_sql
					params = ()
					
					# first row is the header row
					if 0 == i:
						fields = []
						fields_create = []
						for field in row:
							fields.append(field)
							fields_create.append('%s VARCHAR' % field)
						
						create_sql += '(%s)' % ', '.join(fields_create)
						sql = create_sql
						
						insert_sql += '(%s) VALUES (%s)' % (', '.join(fields), ', '.join(['?' for i in xrange(len(fields))]))
					
					# data rows
					else:
						params = tuple(row)
					
					# execute SQL statement
					try:
						sql_cursor.execute(sql, params)
					except Exception as e:
						sys.exit(u'SQL failed: %s  --  %s' % (e, sql))
					i += 1
				
				# commit to file
				sql_handle.commit()
				sql_handle.isolation_level = None
			
			except csv.Error as e:
				sys.exit('CSV error on line %d: %s' % (reader.line_num, e))


# the standard Python CSV reader can't do unicode, here's the workaround
def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
	csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
	for row in csv_reader:
		yield [unicode(cell, 'utf-8') for cell in row]



if '__main__' == __name__:
	csv_file = sys.argv[1]
	print 'csv_file', csv_file
	imp = Importer(csv_file)
	imp.import_to('test.sqlite')
