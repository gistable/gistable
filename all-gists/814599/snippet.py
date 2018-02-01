
from MySQLdb.cursors import SSDictCursor

def iterate_query(query, connection, arraysize=1):
    c = connection.cursor(cursorclass=SSDictCursor)
    c.execute(query)
    while True:
        nextrows = c.fetchmany(arraysize)
        if not nextrows:
            break
        for row in nextrows:
            yield row
    c.close()


results = iterate_query(SQL, conn, arraysize=100)
for row_dict in results:
    print row_dict
