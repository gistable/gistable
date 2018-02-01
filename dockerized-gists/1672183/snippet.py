"""
run with:

    gunicorn -w 1 --worker-class gevent web

open in a browser:

    localhost:8000/consumer
    localhost:8000/consumer
    localhost:8000/producer

Why is it that the consumer requests are queued such that only one is active at
a time while the producer request is allowed to operate concurrently with the
consumer request?  The same behavior is exhibited if you try to run concurrent
producers.
"""

from gevent import monkey
monkey.patch_all()

from gevent import sleep
from gevent import Timeout

from flask import Flask
from flask import Response

from redis import Redis

redis = Redis()
app = Flask(__name__)
application = app  # for easy gunicorn

chanel = "thread_channel:" + str(42)


@app.route('/producer', methods=['POST', 'GET'])
def message_post():
    return Response(producer(), mimetype='application/json')


def producer():
    print "producer"
    for i in xrange(0, 100):
        redis.publish(chanel, i)
        yield [i]
        sleep(.05)


@app.route('/consumer', methods=['GET'])
def thread_get():
    return Response(consumer(), mimetype='application/json')


def consumer():
    print "consumer"
    pubsub = redis.pubsub()
    try:
        with Timeout(30) as timeout:
            pubsub.subscribe(chanel)
            for x in pubsub.listen():
                yield [x['data']]
    except Timeout, t:
        if t is not timeout:
            raise  # not my timeout
        else:
            pubsub.unsubscribe(chanel)


if __name__ == '__main__':
    from gevent import pywsgi
    hp = ('127.0.0.1', 8000)
    server = pywsgi.WSGIServer(hp, app)
    print "Serving on http://%s" % ":".join([str(x) for x in hp])
    server.serve_forever()
