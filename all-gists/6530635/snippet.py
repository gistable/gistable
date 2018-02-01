from django.db import connection
from django.conf import settings
cursor = connection.cursor()
cursor.execute('SHOW TABLES')
results=[]
for row in cursor.fetchall(): 
    results.append(row)

for row in results: 
    cursor.execute('ALTER TABLE %s CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;' % (row[0]))

cursor.execute('ALTER DATABASE %s CHARACTER SET utf8;' % settings.DATABASES['default']['NAME'])


