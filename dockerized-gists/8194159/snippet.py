#! /usr/bin/python
import os
import sys
import urllib2
import re
import sqlite3

def get_mac_table_file(filename="oui.txt"):
	request = urllib2.urlopen("http://standards.ieee.org/develop/regauth/oui/oui.txt")
	with open(filename, "w") as f:
		for line in request:
			f.write(line)

def parse_mac_table_file(filename="oui.txt"):
	ven_arr = []
	with open(filename, "r") as f:
		for line in f:
			if "(base 16)" not in line:
				continue
			ven = tuple(re.sub("\s*([0-9a-zA-Z]+)[\s\t]*\(base 16\)[\s\t]*(.*)\n", r"\1;;\2", line).split(";;"))
			ven_arr.append(ven)
	return ven_arr

def list_to_database(ven_arr, filename="macvendors1.db"):
	try:
		os.unlink(filename)
	except OSError:
		pass
	db = sqlite3.connect(filename)
	cur = db.cursor()
	create_q = "CREATE TABLE macvendors(id INTEGER PRIMARY KEY, mac TEXT, vendor TEXT);"
	cur.execute(create_q)
	query_pr = "INSERT INTO macvendors (`mac`,`vendor`) VALUES "
	query = ""
	for ind, ven in enumerate(ven_arr):
		query = query_pr + '("%s", "%s")\n'% (ven[0], ven[1].replace("\"", "\"\""))
		try:
			cur.execute(query)
		except Exception as e:
			print "Error: %s" % e
			db.close()
			sys.exit()
	db.commit()
	db.close()


if __name__ == "__main__":
	print "Downloading MAC VENDOR list to file oui.txt"
	get_mac_table_file()
	print "Parsing data and inserting in macvendors.db"
	list_to_database(parse_mac_table_file())
	print "Finished"
