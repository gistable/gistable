"""
Copyright (c) 2009, Aaron Bycoffe
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
3. The name of the author may not be used to endorse or promote products
   derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


Example Usage
=============
testcsv.csv is available at http://gist.github.com/217028

>>> table = CSVTable(open(r'testcsv.csv'))
>>> cursor, tablename = table.create()
>>> print tablename
csvtable
>>> cursor.execute("SELECT COUNT(*) FROM %s" % tablename) # doctest:+ELLIPSIS
<sqlite3.Cursor object at 0x...>
>>> print cursor.fetchone()[0]
2836

Even though all columns are stored as text, they can
still be sorted and arithmetic can be performed on them:

>>> cursor.execute("SELECT SUM(latitude) FROM %s" % tablename) # doctest:+ELLIPSIS
<sqlite3.Cursor object at 0x...>
>>> print cursor.fetchone()[0]
109363.189155
>>> response = cursor.execute("SELECT * FROM %s ORDER BY latitude DESC" % tablename)
>>> results = cursor.fetchall()
>>> print results[:5]
[(u'North Slope, AK', u'69.0578758', u'-152.8628274'), (u'Northwest Arctic, AK', u'67.2872981', u'-160.0342625'), (u'Yukon-Koyukuk, AK', u'65.8443667', u'-153.4302993'), (u'Fairbanks North Star, AK', u'64.9526102', u'-146.4744155'), (u'Nome, AK', u'64.502118', u'-165.406729')]

"""

import csv
import sqlite3
import sys


class CSVTable(object):
    """
    Create a sqlite database and table from a CSV file
    for easier querying.

    By default, the database is created in memory.
    A filepath may be passed to the create()
    method if you want to use a file.
    """

    def __init__(self, handler, delimiter=','):
        """By default assume the fields are delimited by commas.

        The first row of input must be the field names.
        """
        self.reader = csv.reader(handler, delimiter=delimiter)


    def create(self, filepath=":memory:", tablename='csvtable'):
        """Create the database and table, and populate it
        with the data from self.reader.
        """
        self.conn = sqlite3.connect(filepath)
        self.cursor = self.conn.cursor()
        self.tablename = tablename

        for row in self.reader:
            if self.reader.line_num == 1:
                self._create_table(row)
                continue
            self._save_data(row)
        return (self.cursor, self.tablename)


    def _create_table(self, row):
        """Create a table in the database.
        """
        createstatement = "CREATE TABLE %s" % self.tablename
        query = '%s (%s)' % (createstatement, 
                             ','.join(['"%s" text' % field for field in row]))
        self.cursor.execute(query)


    def _save_data(self, row):
        query = "INSERT INTO %s VALUES (%s)" % (
                            self.tablename,
                            ','.join(['?' for x in row])
                            )
        self.cursor.execute(query, row)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
