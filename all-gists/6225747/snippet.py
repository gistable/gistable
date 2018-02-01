#!/usr/bin/python

import os
import subprocess
import sqlite3

desktop_picture_path = '/Library/Desktop Pictures/Wave.jpg'
database_location = os.path.expanduser(
    '~/Library/Application Support/Dock/desktoppicture.db')

conn = sqlite3.connect(database_location)
print 'Opened database successfully'

conn.execute('DELETE FROM data')
conn.execute('INSERT INTO data VALUES (?)', (desktop_picture_path, ))
conn.execute('VACUUM data')
conn.commit()

print 'Records created successfully'
conn.close()

subprocess.check_call(['/usr/bin/killall', 'Dock'])