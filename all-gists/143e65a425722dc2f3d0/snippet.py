from impala.dbapi import connect as impala_connect
import csv
import sys
import pdb
import MySQLdb as mysql

global connection
global cursor

def connect():
  global connection, cursor

  connection = impala_connect(host="localhost", port=21050, database="cass")
  cursor = connection.cursor()
  cursor.execute('use cass')

def disconnect():
  global connection
  connection.close()


def export_olark_conversations(start, limit, debug=False):
  global cursor
  
  query = build_query(start, limit)

  if debug:
    print query

  cursor.execute(query)
  conversations = cursor.fetchall();

  # with open('/tmp/olark_conversations.csv', 'ab') as csvfile:
  #   writer = csv.writer(csvfile, delimiter='|')
  #   for conversation in conversations:
  #     writer.writerow(conversation)

  return conversations

def describe_table():
  """
    - feed_time: kapan row tersebut dimasukkan ke impala dari manapun sumbernya

    - time_added: kapan kalimat tersebut dibuat, ketika customer ngobrol dengan
      Customer Service Operator (CSO)

    - date: tanggal kalimat tersebut dibuat, ketika customer ngobrol dengan
      CSO, field ini adalah turunan dari time_added di atas

    - hour: jam tanggal kalimat tersebut dibuat, ketika customer ngobrol dengan
      CSO, field ini adalah turunan dari time_added di atas
  """
  global connection, cursor

  connect();

  cursor.execute('describe cass.olark_conversations');
  descriptions = cursor.fetchall()

  with open('/tmp/olark_conversations_structure.csv', 'wb') as csvfile:
    writer = csv.writer(csvfile, delimiter='|')
    for description in descriptions:
      writer.writerow(description)

  disconnect()

  return description

def build_query(start, limit):
  """
  Tidak bisa mengandalkan kolom `date` karena semakin kemari jumlah obrolan
  semakin banyak. 

  Kolom `time_added` juga tidak bisa diandalkan mengingat ada duplikasi pada
  kolom ini.

  Oleh karena itu digunakan `feed_time` sebagai titik mulai dan di limit
  sejumlah obrolan dari titik tersebut.
  """

  return """
    SELECT conversation_id, id, time_added, feed_time, body
    FROM cass.olark_conversations
    WHERE kind = 'MessageToOperator' AND feed_time >= {start}
    ORDER BY feed_time ASC
    LIMIT {limit}
  """.format(start=start, limit=limit)

def insert_to_mysql(conversations):
  for conversation in conversations:
    try:
      mysql_cursor.execute("""
        INSERT IGNORE INTO unique_conversation (conversation_id, sentence_id, time_added, feed_time, body)
        VALUES (%s, %s, %s, %s, %s)
      """, conversation)

      mysql_connection.commit()

    except mysql.Error as e:
      if mysql_connection:
        mysql_connection.rollback()

      print "Error %d: %s" % (e.args[0], e.args[1])

def insert_to_mysql_many_at_once(conversations):
  """
  MySQLdb tutorial here: http://zetcode.com/db/mysqlpython/
  """
  # pdb.set_trace()

  total = len(conversations)
  per_page = 1000
  pages = (total / per_page) + 1
  page = 1

  while page <= pages:
    offset = ((page - 1) * per_page)
    upper = page * per_page
    _conversations = conversations[offset:upper] # conversations[0:100], conversations[100:200], ...
    _conversations_size = len(_conversations)
    page += 1

    if (_conversations_size > 0):
      try:
        print "inserting {numbers} sentences".format(numbers=_conversations_size)

        mysql_cursor.executemany("""
          INSERT IGNORE INTO unique_conversation (conversation_id, sentence_id, time_added, feed_time, body)
          VALUES (%s, %s, %s, %s, %s)
        """, _conversations)

        mysql_connection.commit()

      except mysql.Error as e:
        if mysql_connection:
          mysql_connection.rollback()

        print "Error %d: %s" % (e.args[0], e.args[1])

mysql_connection = mysql.connect(host="localhost", user="root", db="olark_conversations")
mysql_cursor = mysql_connection.cursor()

try:
  connect()

  # Angka ini didapatkan dari:
  # select feed_time from cass.olark_conversations order by feed_time asc limit 1
  # (bisa saja diberikan dari CLI)
  start = 1440140551
  start = 1440145325
  start = 1446367818
  start = 1446558945
  start = 1450623640
  start = 1450984817
  limit = 100000

  # stop at maximum number of sentences
  maximum = 1000000

  total = 0
  fetch = True
  debug = True

  while fetch and total < maximum:
    conversations = export_olark_conversations(start, limit, debug)

    # update start dengan `feed_time` item paling akhir
    start = conversations[-1][3]

    _total = len(conversations)
    total += _total

    if (_total > 0):
      insert_to_mysql_many_at_once(conversations)
    else:
      fetch = False

    print "Total: {total}".format(total=total)

except Exception as e:
  print e
  print e.args
  sys.exit(1)

finally:
  disconnect()

  if connection:
    connection.close()

  if mysql_connection:
    mysql_connection.close()