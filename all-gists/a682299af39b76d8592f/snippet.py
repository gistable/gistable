from flask import Flask
from flask import g
from flask import Response
from flask import request
import json
import MySQLdb

app = Flask(__name__)

@app.before_request
def db_connect():
  g.conn = MySQLdb.connect(host='192.168.33.10',
                              user='test',
                              passwd='password',
                              db='test')
  g.cursor = g.conn.cursor()

@app.after_request
def db_disconnect(response):
  g.cursor.close()
  g.conn.close()
  return response

def query_db(query, args=(), one=False):
  g.cursor.execute(query, args)
  rv = [dict((g.cursor.description[idx][0], value)
  for idx, value in enumerate(row)) for row in g.cursor.fetchall()]
  return (rv[0] if rv else None) if one else rv

@app.route("/")
def hello():
  return "Hello World!"

@app.route("/names", methods=['GET'])
def names():
  result = query_db("SELECT firstname,lastname FROM test.name")
  data = json.dumps(result)
  resp = Response(data, status=200, mimetype='application/json')
  return resp

@app.route("/add", methods=['POST'])
def add():
  req_json = request.get_json()
  g.cursor.execute("INSERT INTO test.name (firstname, lastname) VALUES (%s,%s)", (req_json['firstname'], req_json['lastname']))
  g.conn.commit()
  resp = Response("Updated", status=201, mimetype='application/json')
  return resp

if __name__ == "__main__":
  app.run()