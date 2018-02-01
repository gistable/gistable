# -*- coding: utf-8 -*-
'''
Created on 2012-09-24

@author: Sergey <me@seriyps.ru>

How to test:

$ head -c 100M /dev/urandom > static_file.bin
$ python
>>> from urllib2 import urlopen
>>>
>>> m100 = 104857600
>>> host = "http://localhost:8888"
>>>
>>> assert len(urlopen(host + "/big_file.bin").read()) == m100
>>> assert len(urlopen(host + "/big_stream.bin").read()) == m100
>>> assert len(urlopen(host + "/big_stream_gen.bin").read()) == m100
>>>
>>> assert len(urlopen(host + "/big_file.bin").read(1024)) == 1024
>>> assert len(urlopen(host + "/big_stream.bin").read(1024)) == 1024
>>> assert len(urlopen(host + "/big_stream_gen.bin").read(1024)) == 1024

This code make tornado consume memory and CPU:

>>> [urlopen(host + "/big_file.bin").read(1) for _ in xrange(100)]

'''
import tornado.ioloop
import tornado.web
import tornado.gen
import os


class FileStreamerHandler(tornado.web.RequestHandler):
    """Standard static file handler loads whole file in memory. This one
    read file chunk-by-chunk."""

    CHUNK_SIZE = 512000         # 0.5 MB

    def initialize(self, file_path):
        self.path = file_path

    @tornado.web.asynchronous
    def get(self):
        self.set_header("Content-Type", "text/plain")
        self.set_header("Content-Length", os.path.getsize(self.path))
        self._fd = open(self.path, "rb")
        self.flush()
        self.write_more()

    def write_more(self):
        data = self._fd.read(self.CHUNK_SIZE)
        if not data:
            self.finish()
            self._fd.close()
            return
        self.write(data)
        self.flush(callback=self.write_more)


class GenFileStreamerHandler(tornado.web.RequestHandler):
    """Standard static file handler loads whole file in memory. This one
    read file chunk-by-chunk."""

    CHUNK_SIZE = 512000         # 0.5 MB

    def initialize(self, file_path):
        self.path = file_path

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        self.set_header("Content-Type", "text/plain")
        self.set_header("Content-Length", os.path.getsize(self.path))
        self.flush()
        # "with" statement didn't work properly in this context (didn't release
        # resources when socket inproperly closed by client)
        # with open(self.path, "rb") as fd:
        #     data = fd.read(self.CHUNK_SIZE)
        #     while data:
        #         self.write(data)
        #         yield tornado.gen.Task(self.flush)
        #         data = fd.read(self.CHUNK_SIZE)
        fd = open(self.path, "rb")
        data = fd.read(self.CHUNK_SIZE)
        while data:
            self.write(data)
            yield tornado.gen.Task(self.flush)
            data = fd.read(self.CHUNK_SIZE)
        fd.close()
        self.finish()


application = tornado.web.Application([
        (r"/(big_file.bin)", tornado.web.StaticFileHandler,
         {"path": "."}),
        (r"/big_stream.bin", FileStreamerHandler,
         {"file_path": "big_file.bin"}),
        (r"/big_stream_gen.bin", GenFileStreamerHandler,
         {"file_path": "big_file.bin"}),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()