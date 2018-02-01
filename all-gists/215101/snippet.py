#! /sw/bin/python
# filename: todosqlite.py
# author: ted heich
# blog: http://fornoobs.info 
#
# A simple todo list app using Python and sqlite using the cmd line interface
# 

#from pysqlite2 import dbapi2 as sqlite
import pysqlite2.dbapi2 as sqlite
import sys

def search():
	if len(sys.argv) > 2:
		search = sys.argv[2]
	
	try:
		sqlstatement = "SELECT task, status, id FROM todo WHERE task LIKE '%" + search + "%';"
		cur.execute(sqlstatement)
		records = cur.fetchall()
		counter = 1
		
		for rec in records:
			counter = counter + 1
		
			if rec[1] == 0:
				status = "(status = nope)"
			else:
				status = "(status = done)"				
			print counter, rec[0], status, "[ID=" ,rec[2],"]"
			
	
	except sqlite.Error, e:
		print "Oooops: ", e.args[0]
	

def list():
	
	sqlstatement = "SELECT task, status, id FROM todo WHERE status = 0"
	
	if len(sys.argv) > 2:
		if sys.argv[2] == "all":
			sqlstatement = "SELECT task, status, id FROM todo;"
		elif sys.argv[2] == "completed":
			sqlstatement = "SELECT task, status, id FROM todo WHERE status <> 0"
			
	try:	
		cur.execute(sqlstatement)
		records = cur.fetchall()
		counter = 0
		for rec in records:
			counter = counter + 1
		
			if rec[1] == 0:
				status = "(status = nope)"
			else:
				status = "(status = done)"				
			print counter, rec[0], status, "[ID=" ,rec[2],"]"
			
	except sqlite.Error, e:
		print "Ooops:", e.args[0]

def add(param):
	try:
		sql = "INSERT INTO todo values(NULL,'" + param + "',0)"
		cur.execute(sql)
		conn.commit()
		print "Affected: %d", cur.rowcount
	except sqlite.Error, e:
		print "Ooops:", e.args[0]

def delete(param):
	
	try:
		cur.execute("DELETE FROM todo WHERE ID='" + param + "'")
		conn.commit()
		print "Affected: %d", cur.rowcount
	except sqlite.Error, e:
		print "Ooops:", e.args[0]
	
def complete(param):
	
	try:
		cur.execute("UPDATE todo set status=1" + " WHERE id=" + param)
		conn.commit()
		print "Affected: %d", cur.rowcount
	except sqlite.Error, e:
		print "Ooops:", e.args[0]

def main():
	
	global conn
	global cur
	
	try:		
		conn = sqlite.connect("todo.sqlite")
		cur = conn.cursor()
	except sqlite.Error, e:
		print "Ooops: ", e.args[0]
		
	if len(sys.argv) == 1 :
		print "Usage is: $td list | add | delete | complete | search"
		sys.exit(0)
	carg = sys.argv[1]
	
	if carg == "add":
		if len(sys.argv) < 3:
			print "You gotta type to the task"
			sys.exit(0)
		add(sys.argv[2])
	elif carg == "delete":
		if len(sys.argv) < 3:
			print "You gotta type the ID to delete"
			sys.exit(0)
		delete(sys.argv[2])
	elif carg == "complete":
		if len(sys.argv) < 3:
			print "You gotta type the ID to mark as complete"
			sys.exit(0)
		complete(sys.argv[2])
	elif carg == "list":
		list()
	elif carg =="search":
		search()
	else:
		print "Gotta type add | delete | list | complete only"
	
if __name__ == "__main__":
	main()
