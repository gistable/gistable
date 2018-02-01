from django.db import connection

# If using cursor without "with" -- it must be closed explicitly:
with connection.cursor() as cursor:
    cursor.execute('select column1, column2, column3 from table where aaa=%s', [5])
    for row in cursor.fetchall():
        print row[0], row[1], row[3]
