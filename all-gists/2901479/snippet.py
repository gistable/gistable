# -*- coding: utf-8 -*-

import os

from flask import Flask

from flask_heroku import Heroku
from flask_sslify import SSLify
from raven.contrib.flask import Sentry
from flask.ext.celery import Celery

app = Flask(__name__)
app.secret_key = os.environ.get('APP_SECRET', 'some-secret-key')
app.debug = 'DEBUG' in os.environ

# Use gevent workers for celery.
app.config['CELERYD_POOL'] = 'gevent'

# Bootstrap Heroku environment variables.
heroku = Heroku(app)

# Redirect urls to https
sslify = SSLify(app)

# Setup error collection
sentry = Sentry(app)

# Task queue
celery = Celery(app)


@app.route('/')
def hello_world():
    return 'Hello World!'
