#!/Users/username/Documents/python/projectname/env/bin/python

# edit line 1 to match what YOU get when you are in YOUR virtualenv and type:  which python
# NO SPACES in first 3 chars in line 1:  #!/
# make sure env is activated! 
# make sure you have "started all" in XAMPP! 
# code below works for a MySQL database in XAMPP on Mac OS
# pymysql can be installed with pip: pip install PyMySQL

import pymysql
from flask import Flask, render_template, session, redirect, url_for
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'some secret string here'

userpass = 'mysql+pymysql://root:@'
basedir  = '127.0.0.1'
dbname   = '/nameofdatabase'
socket   = '?unix_socket=/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock'
dbname   = dbname + socket
app.config['SQLALCHEMY_DATABASE_URI'] = userpass + basedir + dbname

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

# this route will test the database connection and nothing more
@app.route('/')
def testdb():
    if db.session.query('1').from_statement('SELECT 1').all():
        return 'It works.'
    else:
        return 'Something is broken.'

if __name__ == '__main__':
    app.run(debug=True)
