"""Asynchronous requests in Flask with gevent"""

from time import time

from flask import Flask, Response

from gevent.pywsgi import WSGIServer
from gevent import monkey

import requests

# need to patch sockets to make requests async
monkey.patch_all()

CHUNK_SIZE = 1024*1024  # bytes

app = Flask(__name__)  # pylint: disable=invalid-name
app.debug = True


@app.route('/Seattle.jpg')
def seattle(requests_counter=[0]):  # pylint: disable=dangerous-default-value
    """Asynchronous non-blocking streaming of relatively large (14.5MB) JPG
    of Seattle from wikimedia commons.
    """
    requests_counter[0] += 1
    request_num = requests_counter[0]
    url = 'http://upload.wikimedia.org/wikipedia/commons/3/39/Seattle_3.jpg'

    app.logger.debug('started %d', request_num)

    rsp = requests.get(url, stream=True)

    def generator():
        "streaming generator logging the end of request processing"
        yield ''  # to make greenlet switch
        for data in rsp.iter_content(CHUNK_SIZE):
            yield data
        app.logger.debug('finished %d', request_num)

    return Response(generator(), mimetype='image/jpeg')


def main():
    "Start gevent WSGI server"
    # use gevent WSGI server instead of the Flask
    http = WSGIServer(('', 5000), app.wsgi_app)
    # TODO gracefully handle shutdown
    http.serve_forever()


if __name__ == '__main__':
    main()
