'''
chunked_server_test.py

Copyright August 3, 2012
Released into the public domain

This implements a chunked server using Python threads and the built-in
BaseHTTPServer module. Enable gzip compression at your own peril - web
browsers seem to have issues, though wget, curl, Python's urllib2, my own
async_http library, and other command-line tools have no problems.

'''

import BaseHTTPServer
import gzip
import SocketServer
import time

class ChunkingHTTPServer(SocketServer.ThreadingMixIn,
                        BaseHTTPServer.HTTPServer):
    '''
    This is just a proof of concept server that uses threads. You can make it
    fork, maybe hack up a worker thread model, or even use multiprocessing.
    That's your business. But as-is, it works reasonably well for streaming
    chunked data from a server.
    '''
    daemon_threads = True

class ListBuffer(object):
    '''
    This little bit of code is meant to act as a buffer between the optional
    gzip writer and the actual outgoing socket - letting us properly construct
    the chunked output. It also lets us quickly and easily determine whether
    we need to flush gzip in the case where a user has specified
    'ALWAYS_SEND_SOME'.
    
    This offers a minimal interface necessary to back a writing gzip stream.
    '''

    __slots__ = 'buffer',
    def __init__(self):
        self.buffer = []

    def __nonzero__(self):
        return len(self.buffer)

    def write(self, data):
        if data:
            self.buffer.append(data)

    def flush(self):
        pass

    def getvalue(self):
        data = ''.join(self.buffer)
        self.buffer = []
        return data

class ChunkingRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    '''
    Nothing is terribly magical about this code, the only thing that you need
    to really do is tell the client that you're going to be using a chunked
    transfer encoding.

    Gzip compression works partially. See the module notes for more
    information.
    '''
    ALWAYS_SEND_SOME = False
    ALLOW_GZIP = False
    protocol_version = 'HTTP/1.1'
    def do_GET(self):
        ae = self.headers.get('accept-encoding') or ''
        use_gzip = 'gzip' in ae and self.ALLOW_GZIP

        # send some headers
        self.send_response(200)
        self.send_header('Transfer-Encoding', 'chunked')
        self.send_header('Content-type', 'text/plain')

        # use gzip as requested
        if use_gzip:
            self.send_header('Content-Encoding', 'gzip')
            buffer = ListBuffer()
            output = gzip.GzipFile(mode='wb', fileobj=buffer)

        self.end_headers()

        def write_chunk():
            tosend = '%X\r\n%s\r\n'%(len(chunk), chunk)
            self.wfile.write(tosend)

        # get some chunks
        for chunk in chunk_generator():
            if not chunk:
                continue

            # we've got to compress the chunk
            if use_gzip:
                output.write(chunk)
                # we'll force some output from gzip if necessary
                if self.ALWAYS_SEND_SOME and not buffer:
                    output.flush()
                chunk = buffer.getvalue()

                # not forced, and gzip isn't ready to produce
                if not chunk:
                    continue

            write_chunk()

        # no more chunks!

        if use_gzip:
            # force the ending of the gzip stream
            output.close()
            chunk = buffer.getvalue()
            if chunk:
                write_chunk()

        # send the chunked trailer
        self.wfile.write('0\r\n\r\n')

def chunk_generator():
    # generate some chunks
    for i in xrange(10):
        time.sleep(.1)
        yield "this is chunk: %s\r\n"%i

if __name__ == '__main__':
    server = ChunkingHTTPServer(
        ('127.0.0.1', 8080), ChunkingRequestHandler)
    print 'Starting server, use <Ctrl-C> to stop'
    server.serve_forever()
