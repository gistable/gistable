#heroku config:set HEROKU=1

import os
import urlparse
import psycopg2
from flask import Flask
from flask_peewee.db import Database


if 'HEROKU' in os.environ:
    DEBUG = False
    urlparse.uses_netloc.append('postgres')
    url = urlparse.urlparse(os.environ['DATABASE_URL'])
    DATABASE = {
        'engine': 'peewee.PostgresqlDatabase',
        'name': url.path[1:],
        'user': url.username,
        'password': url.password,
        'host': url.hostname,
        'port': url.port,
    }
else:
    DEBUG = True
    DATABASE = {
        'engine': 'peewee.PostgresqlDatabase',
        'name': 'framingappdb',
        'user': 'postgres',
        'password': 'postgres',
        'host': 'localhost',
        'port': 5432 ,
        'threadlocals': True
    }

app = Flask(__name__)
app.config.from_object(__name__)
db = Database(app)