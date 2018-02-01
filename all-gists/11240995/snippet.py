#!/usr/bin/env python2
import os
import tempfile
import sqlite3
 
 
class DBExportor(object):
    def __init__(self, db=None):
        if not db:
            db = self.pullDB()
        self.conn = sqlite3.connect(db)
        self.conn.row_factory = sqlite3.Row
        self.files = {}
 
    def pullDB(self):
        ''' pull Nook Reader's db from device and return the path of that db '''
        db_name = "annotations.db"
        pull_db = "/data/data/com.bn.nook.reader.activities/databases/" + db_name
        db_path = os.path.join(tempfile.gettempdir(), db_name)
        os.system("adb pull %s %s" % (pull_db, db_path))
        return db_path
 
    def saverow(self, row):
        ''' save one row to file '''
        # get fp
        fname = os.path.basename(row['ean'])
        if fname not in self.files:  # create outfile if necessary
            base = os.path.splitext(fname)[0]
            export_file = base + '.txt'
            self.files[fname] = open(export_file, 'w')
        fp = self.files[fname]
 
        # composite a record
        record = "-%s-" % row["pagenumber"]
        if row['highlighttext']:
            record += ' ' + row['highlighttext']
        if row['note']:
            record += ' [Note: %s]' % row['note']
        record += '\n'
 
        # write to file
        fp.write(record.encode('utf8'))
 
    def export_db(self):
        c = self.conn.cursor()
 
        table = "annotations"
        c.execute("SELECT * FROM %s" % table)
        # since pagenumber is a string, need convert to int
        rows = c.fetchall()
        rows.sort(key=lambda c: int(c['pagenumber']))
        for row in rows:
            self.saverow(row)
        c.close()
 
    def cleanup(self):
        self.conn.close()
        for f in self.files.values():
            f.close()
 
    def run(self):
        self.export_db()
        self.cleanup()
 
 
if __name__ == '__main__':
    exp = DBExportor()
    exp.run()
