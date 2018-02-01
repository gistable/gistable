#!/usr/bin/python
# coding: UTF-8

import MySQLdb
import signal, os, sys

workers = {}
END_SIGNAL = "\n"

def connect():
  con = MySQLdb.connect(host='localhost', db='test', user='testuser', passwd='password')
  return con

def get_mysql_pid(con):
  cur = con.cursor()
  cur.execute('SELECT CONNECTION_ID()') #自分自身のmysqlセッションを取得
  return cur.fetchall()[0][0]

def kill_mysql_pid(con,mysql_pid):
  cur = con.cursor()
  cur.execute('KILL ' + mysql_pid) #mysqlセッションをKILL

def run(con, query):
  signal.signal(signal.SIGTERM, lambda sig, status: sys.exit(0))
  cur = con.cursor()
  cur.execute(query)

def killall(sig, status):
  con = connect()
  for pid in workers.keys():
    kill_mysql_pid(con,workers[pid]) #子プロセスのmysqlセッションをKILLする
    os.kill(pid, signal.SIGTERM)

def waitall():
  for pid in workers.keys():
    try:
      os.waitpid(pid, 0)
    except:
      print "waitpid: interrupted exception"

def main():
  signal.signal(signal.SIGINT, killall)
  signal.signal(signal.SIGTERM, killall)
  r_num, w_num = os.pipe()
  pid = os.fork()
  if pid == 0:
    os.close(r_num)
    wpipe = os.fdopen(w_num, 'w')
    con = connect()
    mysql_pid = "%d\n" % get_mysql_pid(con) #親プロセスへ子プロセスのmysqlセッションidを送る
    wpipe.write(mysql_pid)
    wpipe.flush()
    try:
      run(con, "SELECT SLEEP(30)")
    except:
      print "run: interrupted exception"
      sys.exit(0)
  else:
    os.close(w_num)
    rpipe = os.fdopen(r_num, 'r')
    mysql_pid = rpipe.readline()
    mysql_pid = mysql_pid[:-1]
    workers[pid] = mysql_pid #子プロセスのmysqlセッションidを保存しておく
    print workers[pid]
  waitall()

if __name__ == '__main__':
  main()
