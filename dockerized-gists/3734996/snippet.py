from flask import Flask, url_for, render_template, g, redirect
import random
import sqlite3

DATABASE = 'quotes.db'

app = Flask(__name__)

def connect_db():
	return sqlite3.connect(DATABASE)

@app.before_request
def before_request():
	g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
	if hasattr(g, 'db'):
		g.db.close()

def get_connection():
	db  = getattr(g, '_db', None)
	if db is None:
		db = g._db = connect_db()
	return db

def query_db(query, args=(), one=False):
	cur = g.db.execute(query, args)
	rv = [dict((cur.description[idx][0], value) for idx, value in enumerate(row)) for row in cur.fetchall()]
	return (rv[0] if rv else None) if one else rv


@app.route('/')
def index():
	def generate_quote():
		ids = [i['id'] for i in query_db('SELECT id from quotes')]
		index = int(random.randint(0,len(ids)))
		randquery = 'SELECT * FROM quotes WHERE id == '+str(ids[index])
		print randquery
		result = query_db(randquery)
		return result[0]['quote']
	try:
		quote = generate_quote()
	except:
		quote = 'Random Quote Goes Here'
	return render_template('main.html', quote=quote)

@app.route('/quote/<id>')
def show_quote_by_id(id):
	quote = 'You fail.'
	def get_quote(id):
		ids = [i['id'] for i in query_db('SELECT id from quotes')]
                if int(id) < 0 or int(id) > len(ids):
			redirect('page_not_found')
		out = query_db('SELECT * FROM quotes WHERE id =='+str(ids[int(id)]))
		print out
		return out[0]['quote']
	try:
		quote = get_quote(id)
	except:
		redirect(url_for('index'))
	return render_template('main.html', quote=quote)

@app.errorhandler(404)
def not_found(error):
	return render_template('error.html'), 404

if __name__ == "__main__":
	app.debug = True
	app.run()
