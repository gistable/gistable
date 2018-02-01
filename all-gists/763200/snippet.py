#!/usr/bin/env python

from sys import argv
from hashlib import sha1
from cStringIO import StringIO

class githash(object):
    def __init__(self):
        self.buf = StringIO()

    def update(self, data):
        self.buf.write(data)

    def hexdigest(self):
        data = self.buf.getvalue()
        h = sha1()
        h.update("blob %u\0" % len(data))
        h.update(data)

        return h.hexdigest()

def githash_data(data):
    h = githash()
    h.update(data)
    return h.hexdigest()

def githash_fileobj(fileobj):
    return githash_data(fileobj.read())


if __name__ == '__main__':
    for filename in argv[1:]:
        fileobj = file(filename)
        print(githash_fileobj(fileobj))
