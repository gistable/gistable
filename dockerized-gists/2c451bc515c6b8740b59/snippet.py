# Unlike Twisted, Tulip and Tornado, gevent can use existing Python libraries:
# Django, Flask, requests, redis-py, SQLAlchemy to name a few
from gevent import monkey; monkey.patch_all()
import gevent

import requests
from flask import Flask
app = Flask(__name__)


@app.route('/')
def hello_world():
    return requests.get('http://python.org').content


if __name__ == '__main__':
    from gevent import pywsgi
    import signal
    server = pywsgi.WSGIServer(':8000', app)
    server.start()

    # graceful shutdown: sending SIGINT/SIGTERM would close the listener
    # but keep the process running until the last connection closed
    gevent.signal(signal.SIGINT, server.close)
    gevent.signal(signal.SIGTERM, server.close)
    gevent.wait()