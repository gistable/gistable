# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from StringIO import StringIO
import pprint as pprint
import sys


# Original idea: http://softwaremaniacs.org/forum/python/25696/
class DecoderStream:

    def __init__(self, stream):
        self._stream = stream

    def write(self, s):
        s = s.decode('unicode_escape').encode('utf-8')
        return self._stream.write(s)


# TODO: Use the custom decoder only if six.PY3 is False
def unipprint(obj, stream=None, **kwargs):
    if stream is None:
        stream = sys.stdout
    pprint.pprint(obj, DecoderStream(stream), **kwargs)


def unipformat(obj, **kwargs):
    stream = StringIO()
    kwargs['stream'] = stream
    unipprint(obj, **kwargs)
    return stream.getvalue().decode('utf-8')
