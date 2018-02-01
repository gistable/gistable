#!/usr/bin/env python
import MySQLdb

import os, sys
import pprint
pp = pprint.PrettyPrinter()

mysql_host = "localhost"
mysql_user = "dbusername"
mysql_pass = "dbpassword"
mysql_db = "powerdns"



#ClientIP, ClientMac, host-decl-name
if (len(sys.argv) > 1):

	command = sys.argv[1]
	clientIP = sys.argv[2]
	clientMac = sys.argv[3]
	hostname = sys.argv[4]

	if command == "commit":
		f = open("/tmp/leases",'a')
		s = "Leased: %s to %s\n" % (clientIP, hostname)
		f.write(s)
		f.flush()
		f.close()

		db = MySQLdb.connect(host=mysql_host, user=mysql_user, passwd=mysql_pass, db=mysql_db)
                cursor = db.cursor()
		cursor.execute("INSERT INTO records (domain_id,name,type,content,ttl,prio,change_date) VALUES (%s,%s,%s,%s,%s,%s,UNIX_TIMESTAMP(NOW()))", [1,hostname,"A",clientIP,3600,0])
#		pp.pprint(cursor.__dict__)
		cursor.close()
		db.commit()
		db.close()
	elif command == "release":
		f = open("/tmp/leases",'a')
		s = "Released: %s from %s\n" % (clientIP, hostname)
		f.write(s)
		f.flush()
		f.close()
		db = MySQLdb.connect(host=mysql_host, user=mysql_user, passwd=mysql_pass, db=mysql_db)
                cursor = db.cursor()
		cursor.execute("DELETE FROM records WHERE content = %s AND name = %s",[clientIP,hostname])
		#pp.pprint(cursor.__dict__)
		db.commit()
		db.close()
	elif command == "expiry":
		f = open("/tmp/leases",'a')
                s = "Expired: %s from %s\n" % (clientIP, hostname)
                f.write(s)
                f.flush()
                f.close()
		db = MySQLdb.connect(host=mysql_host, user=mysql_user, passwd=mysql_pass, db=mysql_db)
                cursor = db.cursor()
		cursor.execute("DELETE FROM records WHERE content = %s AND name = %s",[clientIP,hostname])
		#pp.pprint(cursor.__dict__)
		db.commit()
		db.close()
	
