import MySQLdb

##
# @author Jay Taylor [@jtaylor]
# @date 2010-11-15
#
# @description This is a basic database helper script which will setup the connection.
#
# @requirements The MySQLdb package must be installed, i.e. `sudo easy_install MySQLdb`
#
# @example Execute a SELECT query.
#    import MySQLdb
#    from dbhelper import *
#
#    def fetchMatchingPostIds(gmtTs, url):
#        # Fetch a connection to the database.
#        conn = getConn()
#
#        # Setup the cursor.
#        cursor = setup_cursor(conn.cursor())
#
#        # Generate the SQL query.
#        sql = ''' 
#            SELECT id
#            FROM myDb.posts
#            WHERE postType = 'post'
#                AND postDateGmt = %s
#                AND guid like %s
#        ''' % ( 
#            conn.literal(gmtTs), conn.literal('%' + url + '%')
#        )
#
#        # Execute query.
#        cursor.execute(sql)
#
#        # Iterate over results and populate output.
#        results = [x[0] for x in cursor.fetchall()]
#
#        # Cleanup the cursor.
#        cursor.close()
#
#        # Return the results.
#        return results
#
#    if __name__ == '__main__':
#        print fetchMatchingPostIds('2012-03-13 12:01:01', 'google.com', 
#        
#
# @example Add an index to a table.
#    import MySQLdb
#    from dbhelper import *
#
#    conn = getConn()
#    cursor = setup_cursor(conn.cursor(MySQLdb.cursors.DictCursor))
#    sql = 'ALTER TABLE myTable ADD UNIQUE (colName1, colName2)'
#    try:
#        cursor.execute(sql)
#        print 'UNIQUE KEY SUCCESSFULLY ADDED TO WP_POSTS! GOOD JOB.'
#                break
#    except MySQldb.IntegrityError, e:
#        print 'Caught integrity error: %s' % e
#    except Exception, e:
#        print 'Caught exception: %s' % e
#


DB_CONFIG = {
    'name': '<NAME_OF_DB>',
    'host': '<DB_HOSTNAME>',
    'user': '<DB_USERNAME>',
    'pass': '<DB_PASSWORD>'
}

def getConn():
    conn = MySQLdb.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        passwd=DB_CONFIG['pass'],
        db=DB_CONFIG['name'],
        charset='utf8',
        use_unicode=True,
    )
    conn.set_character_set('utf8')
    return conn


def setup_cursor(dbc):
    dbc.execute('SET NAMES utf8;')
    dbc.execute('SET CHARACTER SET utf8;')
    dbc.execute('SET character_set_connection=utf8;')
    return dbc