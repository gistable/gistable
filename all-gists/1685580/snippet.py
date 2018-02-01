from flask import Flask, g, request, flash, url_for, redirect, render_template, abort
from flaskext.jsonify import jsonify
from flaskext.sqlalchemy import *
from sqlalchemy import *
from pyodbc import *
import logging

DATABASE = "dsn=Foo;Trusted_Connection=Yes"
SECRET_KEY = "asdasdfasd1234sdagfa23asdfg123"

app = Flask(__name__)
app.config.from_object(__name__)
db = SQLAlchemy(app)
app.debug = True

logging.basicConfig(filename='strava.log',level=logging.DEBUG)

def connect_db():
	logging.warning("connect_db")
	return create_engine('mssql+pyodbc://Foo').connect()
    #return pyodbc.connect(app.config['DATABASE'])

@app.before_request
def before_request():
	logging.warning("before_request")
	g.db = connect_db()
	logging.info(type(g.db))
	if g.db is None:
		logging.error("No database to connect to")
	else:
		logging.info("Database successfully created ")
		

@app.teardown_request
def teardown_request(exception):
	logging.warning("teardown_request")
	if hasattr(g, 'db'):
		g.db.close()
	#pass

def dump_datetime(value):
	"""Deserialize datetime object into string form for JSON processing."""
	if value is None:
		return None
	return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]


#@app.route("/")
#def hello():
#    return "Hello fsda fs World!"

@app.route('/')
@jsonify
def index():
	logging.info("entering index")	
	cur = g.db.execute('select * from Requisitions')
	logging.info("has data")	
	results = cur.fetchall()
	entries = [dict(title=row['title'], text=row[1]) for row in results]
	entries2 = results
	logging.info("has entries")	
	return entries

@app.route('/api/<message>')
def get_results(message):
	#response = render_template('%s.html' % message )
	try:
		with open('json/%s.json' % message) as f:
			return f.read(), 200, {'Content-Type': 'application/json'}
	except:
		return json_error("Invalid message request", "500"), 406, {'Content-Type': 'application/json'}
	
def json_error(message, error_code):
	return "{'success': 'false', 'message': '%s', 'code': '%s'}" % (message, error_code)

if __name__ == "__main__":
    app.run()
