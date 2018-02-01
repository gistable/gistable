import gevent
import gevent.monkey
gevent.monkey.patch_all()

from gevent.pywsgi import WSGIServer
from flask import Flask


app = Flask(__name__)
app.debug = True

# Simple catch-all server
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    return 'It is Working!'

def background():
    count = 0
    while True:
        print count
        count += 1
        gevent.sleep(1)

if __name__ == '__main__':
    http_server = WSGIServer(('', 4430), app, keyfile='server.key', certfile='server.crt')
    srv_greenlet = gevent.spawn(http_server.start)
    background_task = gevent.spawn(background)
    try:
        gevent.joinall([srv_greenlet, background_task])
    except KeyboardInterrupt:
        print "Exiting"
