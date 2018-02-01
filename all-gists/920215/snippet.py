"""A couple of very simple utilities for reading and writing files
that contain multiple JSON values. Could be useful in situations where
you're generating a bunch of data for later processing and then, later,
you want to read it in an element at a time.

The json module doesn't really support streaming reads, though, so this
is limited by that. If you need real streaming, you probably want to use
something like ijson:
    http://pypi.python.org/pypi/ijson/
"""
import json
import StringIO

_decoder = json.JSONDecoder()
_encoder = json.JSONEncoder()
_space = '\n'

def dump(fp, iterable):
    """Write a sequence of values to a file-like object."""
    for obj in iterable:
        for chunk in _encoder.iterencode(obj):
            fp.write(chunk)
        fp.write(_space)

def dumps(iterable):
    """Like `dump` but returns a string."""
    fp = StringIO.StringIO()
    dump(fp, iterable)
    return fp.getvalue()

def loads(s):
    """A generator reading a sequence of JSON values from a string."""
    while s:
        s = s.strip()
        obj, pos = _decoder.raw_decode(s)
        if not pos:
            raise ValueError('no JSON object found at %i' % pos)
        yield obj
        s = s[pos:]

def load(fp):
    """Like `loads` but reads from a file-like object."""
    return loads(fp.read())
