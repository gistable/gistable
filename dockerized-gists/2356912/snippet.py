# nanoshorten - a very tiny URL shortener Web application written in Bottle and sqlite
# copyright (c) 2012 darkf
# licensed under the WTFPL (WTF Public License)
# see http://sam.zoy.org/wtfpl/ for details

from bottle import get, request, run
import sqlite3, random, string

con = sqlite3.connect('short.db')
c = con.cursor()
c.execute('create table if not exists urls (url VARCHAR(255), shortened VARCHAR(64))')
con.commit()

def shorten(url):
	s = ''.join([random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for x in xrange(10)])
	c.execute('insert into urls (url, shortened) values (?, ?)', (url, s))
	con.commit()
	return s

def unshorten(s):
	for row in c.execute('select url from urls where shortened = ?', (s,)):
		return row[0]
	return 'not found'

@get('/s')
def s():
	if not request.query.url:
		return 'Enter a URL: <form method="get" action="s"><input type="text" name="url"><input type="submit" value="Shorten"></form>'
	return "http://%s/%s" % (request.environ['HTTP_HOST'], shorten(request.query.url))

@get('/<url>')
def root(url):
	return unshorten(url)

run()