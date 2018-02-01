#!/usr/bin/env python
#
# Scripts download oui.txt from web and load data to PostgreSQL database.
#
# Dariusz Pawlak <pawlakdp@gmail.com>
# 2014.05.16
#
#
import re
import urllib
#
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2 import errorcodes
#
# PgSQl connection
#
DBHOST=""
DBNAME=""
DBUSER=""
DBPSWD=""
"""

SQL minimal table needed by script:

-- Table: TABLENAME

-- DROP TABLE TABLENAME;

CREATE TABLE TABLENAME
(
  oui character varying(8) NOT NULL,
  vendor character varying NOT NULL,
  id serial NOT NULL,
  CONSTRAINT pk_mac_vendors PRIMARY KEY (oui)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE TABLENAME
  OWNER TO DBUSER;
  
"""
#
OUI_URL = "http://standards.ieee.org/develop/regauth/oui/oui.txt"
OUI_FILE = "oui.txt"
#
#
if __name__ == "__main__":
    #
    # download oui.txt
    #print "Downloading ",OUI_URL
    #urllib.urlretrieve(OUI_URL, OUI_FILE)
    #
    #connect to db
    try:
	conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (DBNAME,DBUSER,DBHOST,DBPSWD))
    except:
	sys.exit("I am unable to connect to the database")
    #
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    # parsing oui.txt data
    print "Parsing data..."
    with open(OUI_FILE) as infile:
	for line in infile:
	    #do_something_with(line)
	    if re.search("(hex)", line):
		try:
		    mac,vendor = line.strip().split("(hex)")
		except:
		    mac = vendor = ''
		#print line.strip().split("(hex)")
		#print mac.strip().replace("-",":").lower(), vendor.strip()
		if mac!='' and vendor!='':
		    sql = "INSERT INTO mac_vendors "
		    sql+= "(oui,vendor) "
		    sql+= "VALUES ("
		    sql+= "'%s'," % mac.strip().replace("-",":").lower()
		    sql+= "'%s'" % vendor.strip().replace("'","`")
		    sql+= ")"
		    print sql
		    try:
			cur.execute(sql)
		    except Exception, e:
			print "Not inserted because error: ",errorcodes.lookup(e.pgcode)
			
    #
    cur.close()
    conn.close()
#
# EOF
#