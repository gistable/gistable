import mysql.connector
uuids = []
class MySQLCursorDict(mysql.connector.cursor.MySQLCursor):
        def _row_to_python(self, rowdata, desc=None):
                row = super(MySQLCursorDict, self)._row_to_python(rowdata, desc)
                if row:
                        return dict(zip(self.column_names, row))
                return None

cnx = mysql.connector.connect(host="localhost", user="glance", passwd="", db="glance")
cur1 = cnx.cursor(cursor_class=MySQLCursorDict)
cur2 = cnx.cursor(cursor_class=MySQLCursorDict)
cur3 = cnx.cursor(cursor_class=MySQLCursorDict)
cur4 = cnx.cursor(cursor_class=MySQLCursorDict)
cur5 = cnx.cursor(cursor_class=MySQLCursorDict)
cur = cnx.cursor(cursor_class=MySQLCursorDict)
cur.execute("SELECT * FROM  `images` WHERE  `deleted_at` IS NOT NULL")
for row in cur.fetchall():
        uuids.append( row['id']);

cur5.execute("SET FOREIGN_KEY_CHECKS = 0;")

for uuid in uuids:
        cur.execute("show tables");
        for table_name in cur.fetchall():
                if (table_name['Tables_in_glance'] != 'services'):
                        cur2.execute("SELECT column_name FROM information_schema.columns WHERE TABLE_SCHEMA='glance' and table_name='%s';" % table_name['Tables_in_glance'])
                        for column_name in cur2.fetchall():
                                cur3.execute("SELECT * from `%s` WHERE `%s` like '%s';" % (table_name['Tables_in_glance'], column_name['column_name'], uuid))
                                lastq = cur3.fetchall()
                                if(len(lastq) > 0):
                                        print "%s => %s => %s" % (table_name['Tables_in_glance'], column_name['column_name'], uuid)
                                        #print "DELETE FROM `%s` WHERE `%s` like '%s';" % (table_name['Tables_in_glance'], column_name['column_name'], uuid)
                                        cur4.execute("DELETE FROM `%s` WHERE `%s` like '%s';" % (table_name['Tables_in_glance'], column_name['column_name'], uuid))
        cnx.commit()

        print uuid
        print "___________________________________"

cur5.execute("SET FOREIGN_KEY_CHECKS = 1;")
cnx.close()
