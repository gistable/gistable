# -*- coding: utf-8 -*-

import cgi,sqlite3,datetime
from wsgiref.simple_server import make_server

LIMIT=50  # 最大表示記事数.
DB_FILE='/sdcard/bbs.sqlite'

con=sqlite3.connect(DB_FILE)
cur=con.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS bbs (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, user TEXT, datetime TEXT, data TEXT)')
INSERT_DB='INSERT INTO bbs VALUES(NULL,?,?,?)'

def post(user,data):
  if data=='': return
  if user=='': user='匿名'
  dt=datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
  cur.execute(INSERT_DB,(cgi.escape(user.decode('utf-8')),dt,cgi.escape(data.decode('utf-8')).replace('\n','<br />')))
  con.commit()

def bbs(environ,start_response):
  if environ['PATH_INFO']=='/':
    if environ['REQUEST_METHOD']=='POST':
      fs=cgi.FieldStorage(fp=environ['wsgi.input'],environ=environ,keep_blank_values=1)
      post(fs.getfirst('user','').strip(),fs.getfirst('data','').strip())
    data=u'<html><head><title>BBS by Android</title></head><body><form action="/" method="post"><div><textarea name="data" cols="40" rows="5"></textarea></div><span>名前:<input type="text" name="user" size="20" maxlength="30" /></span> <span><input type="submit" name="submit" value="送信" /></span> <span><input type="button" value="更新" onclick="location.reload(true);" /></span></form>'
    cur.execute('SELECT * FROM bbs ORDER BY id DESC')
    for i, row in enumerate(cur):
      if i>=LIMIT: break
      data+=('<div><p>%d <b>%s</b> %s</p><p>%s</p></div>' % row)
    data+='</body></html>'
    start_response('200 OK',[('Content-type','text/html;charset=utf-8')])
    return [data.encode('utf-8')]

httpd=make_server('',8080,bbs)
httpd.serve_forever()
