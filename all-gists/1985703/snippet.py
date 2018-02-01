# -*- coding: utf-8 -*-
"""
    Flaskr
    ~~~~~~

    A microblog example application written as Flask tutorial with
    Flask and couchdbkit.

    :copyright: (c) 2010 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""
# $ mkdir flaskr
# $ cd flaskr
# $ virtualenv env
# $ source env/bin/activate
# $ pip install Flask
# $ pip install couchdbkit
# $ python
# >>> import flaskr
# >>> flaskr.init_db()
# >>> quit()
# $ python flaskr.py
# http://localhost:5000/
# http://localhost:5984/_utils/database.html?flaskr

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

import datetime
from couchdbkit import Document, StringProperty, DateTimeProperty
import couchdbkit
import logging


# configuration
DATABASE = 'flaskr'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


# ppa:randall-leeds/couchdb
# $ apt-get update
# $ sudo apt-get install couchdb

def connect_db():
    """Returns a new connection to the database."""
    server = couchdbkit.Server()
    return server.get_or_create_db(app.config['DATABASE'])


# $ python
# >>> from flaskr import init_db
# >>> init_db()

def init_db():
    """Creates the database views."""
    db = connect_db()
    loader = couchdbkit.loaders.FileSystemDocsLoader('_design')
    loader.sync(db, verbose=True)


class Entry(Document):
    author = StringProperty()
    date = DateTimeProperty()
    title = StringProperty()
    text = StringProperty()



@app.before_request
def before_request():
    """Make sure we are connected to the database each request."""
    g.db = connect_db()
    Entry.set_db(g.db)



@app.teardown_request
def teardown_request(exception):
    """Closes the database again at the end of the request."""
#    if hasattr(g, 'db'):
#        g.db.close()
    # couchdbkit close ?


@app.route('/')
def show_entries():
    # ? entries = Entry.view('entry/all')
    entries = g.db.view('entry/all', schema=Entry)
    app.logger.debug(entries.all())
    return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    app.logger.debug('before')
    entry = Entry(author='test', title=request.form['title'], text=request.form['text'], date=datetime.datetime.utcnow())
    app.logger.debug('after')
    g.db.save_doc(entry)
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

app.debug = True
app.logger.setLevel(logging.INFO)


#logging.basicConfig(filename='example.log',level=logging.INFO)
couchdbkit.set_logging('info')

if __name__ == '__main__':
    app.run()
