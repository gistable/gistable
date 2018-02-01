#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Inspired by:
* http://weeklybuild.com/2014/07/07/mjpeg-bottle-gstreamer/
* http://www.ridgesolutions.ie/index.php/2014/11/24/streaming-mjpeg-video-with-web2py-and-python/
* https://gist.github.com/n3wtron/4624820
'''

from gevent import monkey; monkey.patch_all()
from bottle import route, response, run
from time import sleep

BOUNDARY = "arflebarfle"
CRLF = "\r\n"

class MJPEG(object):

    counter = 0;

    def __init__(self):
        pass

    def __iter__(self):
        return self

    def next(self):
        sleep(30.0 / 1000)

        # Read a jpeg frame
        data = open("rc/image_" + "{0:04d}".format(self.counter) + ".jpg", 'rb').read()

        self.counter += 1

        # Add the frame boundary to the output
        out = "--" + BOUNDARY + CRLF

        # Add the jpg frame header
        out += "Content-type: image/jpeg" + CRLF

        # Add the frame content length
        out += "Content-length: " + str(len(data)) + CRLF + CRLF

        # Add the actual binary jpeg frame data
        return out + data

    def stop(self):
        pass


@route('/')
def index():
    return '<html><body><img src="/mjpeg" /></body></html>'

@route('/mjpeg')
def mjpeg():
    response.content_type = "multipart/x-mixed-replace;boundary=" + BOUNDARY
    return iter(MJPEG())


run(host='0.0.0.0', port=8000, debug=True)
