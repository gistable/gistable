# encoding: utf-8

# FastCGI-to-WSGI bridge for files/pipes transport (not socket)
#
# Copyright (c) 2002, 2003, 2005, 2006 Allan Saddi <allan@saddi.com>
# Copyright (c) 2011 Ruslan Keba <ruslan@helicontech.com>
# Copyright (c) 2012 Antoine Martin <antoine@openance.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#

__author__ = 'Allan Saddi <allan@saddi.com>, Ruslan Keba <ruslan@helicontech.com>, Antoine Martin <antoine@openance.com>'

import msvcrt
import struct
import os
import os.path
import logging
import sys
import traceback
import datetime
import urllib
from optparse import OptionParser
from django.core.management.base import BaseCommand
from django.conf import settings


# Constants from the spec.

FCGI_LISTENSOCK_FILENO = 0
FCGI_HEADER_LEN = 8
FCGI_VERSION_1 = 1
FCGI_BEGIN_REQUEST = 1
FCGI_ABORT_REQUEST = 2
FCGI_END_REQUEST = 3
FCGI_PARAMS = 4
FCGI_STDIN = 5
FCGI_STDOUT = 6
FCGI_STDERR = 7
FCGI_DATA = 8
FCGI_GET_VALUES = 9
FCGI_GET_VALUES_RESULT = 10
FCGI_UNKNOWN_TYPE = 11
FCGI_MAXTYPE = FCGI_UNKNOWN_TYPE
FCGI_NULL_REQUEST_ID = 0
FCGI_KEEP_CONN = 1
FCGI_RESPONDER = 1
FCGI_AUTHORIZER = 2
FCGI_FILTER = 3
FCGI_REQUEST_COMPLETE = 0
FCGI_CANT_MPX_CONN = 1
FCGI_OVERLOADED = 2
FCGI_UNKNOWN_ROLE = 3

FCGI_MAX_CONNS = 'FCGI_MAX_CONNS'
FCGI_MAX_REQS = 'FCGI_MAX_REQS'
FCGI_MPXS_CONNS = 'FCGI_MPXS_CONNS'

FCGI_Header = '!BBHHBx'
FCGI_BeginRequestBody = '!HB5x'
FCGI_EndRequestBody = '!LB3x'
FCGI_UnknownTypeBody = '!B7x'

FCGI_EndRequestBody_LEN = struct.calcsize(FCGI_EndRequestBody)
FCGI_UnknownTypeBody_LEN = struct.calcsize(FCGI_UnknownTypeBody)

FCGI_HEADER_NAMES = (
    'ERROR TYPE: 0',
    'BEGIN_REQUEST',
    'ABORT_REQUEST',
    'END_REQUEST',
    'PARAMS',
    'STDIN',
    'STDOUT',
    'STDERR',
    'DATA',
    'GET_VALUES',
    'GET_VALUES_RESULT',
    'UNKNOWN_TYPE',
)

FCGI_DEBUG = getattr(settings, 'FCGI_DEBUG', settings.DEBUG)
FCGI_LOG = getattr(settings, 'FCGI_LOG', FCGI_DEBUG)
FCGI_LOG_PATH = getattr(settings, 'FCGI_LOG_PATH', os.path.dirname(os.path.abspath(sys.argv[0])))

class InputStream(object):
    """
    File-like object representing FastCGI input streams (FCGI_STDIN and
    FCGI_DATA). Supports the minimum methods required by WSGI spec.
    """

    def __init__(self, conn):
        self._conn = conn

        # See Server.
        self._shrinkThreshold = conn.server.inputStreamShrinkThreshold

        self._buf = ''
        self._bufList = []
        self._pos = 0 # Current read position.
        self._avail = 0 # Number of bytes currently available.

        self._eof = False # True when server has sent EOF notification.

    def _shrinkBuffer(self):
        """Gets rid of already read data (since we can't rewind)."""
        if self._pos >= self._shrinkThreshold:
            self._buf = self._buf[self._pos:]
            self._avail -= self._pos
            self._pos = 0

            assert self._avail >= 0

    def _waitForData(self):
        """Waits for more data to become available."""
        self._conn.process_input()

    def read(self, n=-1):
        if self._pos == self._avail and self._eof:
            return ''
        while True:
            if n < 0 or (self._avail - self._pos) < n:
                # Not enough data available.
                if self._eof:
                    # And there's no more coming.
                    newPos = self._avail
                    break
                else:
                    # Wait for more data.
                    self._waitForData()
                    continue
            else:
                newPos = self._pos + n
                break
            # Merge buffer list, if necessary.
        if self._bufList:
            self._buf += ''.join(self._bufList)
            self._bufList = []
        r = self._buf[self._pos:newPos]
        self._pos = newPos
        self._shrinkBuffer()
        return r

    def readline(self, length=None):
        if self._pos == self._avail and self._eof:
            return ''
        while True:
            # Unfortunately, we need to merge the buffer list early.
            if self._bufList:
                self._buf += ''.join(self._bufList)
                self._bufList = []
                # Find newline.
            i = self._buf.find('\n', self._pos)
            if i < 0:
                # Not found?
                if self._eof:
                    # No more data coming.
                    newPos = self._avail
                    break
                else:
                    if length is not None and len(self._buf) >= length + self._pos:
                        newPos = self._pos + length
                        break
                        # Wait for more to come.
                    self._waitForData()
                    continue
            else:
                newPos = i + 1
                break
        r = self._buf[self._pos:newPos]
        self._pos = newPos
        self._shrinkBuffer()
        return r

    def readlines(self, sizehint=0):
        total = 0
        lines = []
        line = self.readline()
        while line:
            lines.append(line)
            total += len(line)
            if 0 < sizehint <= total:
                break
            line = self.readline()
        return lines

    def __iter__(self):
        return self

    def next(self):
        r = self.readline()
        if not r:
            raise StopIteration
        return r

    def add_data(self, data):
        if not data:
            self._eof = True
        else:
            self._bufList.append(data)
            self._avail += len(data)


class OutputStream(object):
    """
    FastCGI output stream (FCGI_STDOUT/FCGI_STDERR). By default, calls to
    write() or writelines() immediately result in Records being sent back
    to the server. Buffering should be done in a higher level!
    """

    def __init__(self, conn, req, type, buffered=False):
        self._conn = conn
        self._req = req
        self._type = type
        self._buffered = buffered
        self._bufList = [] # Used if buffered is True
        self.dataWritten = False
        self.closed = False

    def _write(self, data):
        length = len(data)
        while length:
            to_write = min(length, self._req.server.maxwrite - FCGI_HEADER_LEN)

            rec = Record(self._type, self._req.requestId)
            rec.contentLength = to_write
            rec.contentData = data[:to_write]
            self._conn.writeRecord(rec)

            data = data[to_write:]
            length -= to_write

    def write(self, data):
        assert not self.closed

        if not data:
            return

        self.dataWritten = True

        if self._buffered:
            self._bufList.append(data)
        else:
            self._write(data)

    def writelines(self, lines):
        assert not self.closed

        for line in lines:
            self.write(line)

    def flush(self):
        # Only need to flush if this OutputStream is actually buffered.
        if self._buffered:
            data = ''.join(self._bufList)
            self._bufList = []
            self._write(data)

    # Though available, the following should NOT be called by WSGI apps.
    def close(self):
        """Sends end-of-stream notification, if necessary."""
        if not self.closed and self.dataWritten:
            self.flush()
            rec = Record(self._type, self._req.requestId)
            self._conn.writeRecord(rec)
            self.closed = True


class TeeOutputStream(object):
    """
    Simple wrapper around two or more output file-like objects that copies
    written data to all streams.
    """

    def __init__(self, streamList):
        self._streamList = streamList

    def write(self, data):
        for f in self._streamList:
            f.write(data)

    def writelines(self, lines):
        for line in lines:
            self.write(line)

    def flush(self):
        for f in self._streamList:
            f.flush()


class StdoutWrapper(object):
    """
    Wrapper for sys.stdout so we know if data has actually been written.
    """

    def __init__(self, stdout):
        self._file = stdout
        self.dataWritten = False

    def write(self, data):
        if data:
            self.dataWritten = True
        self._file.write(data)

    def writelines(self, lines):
        for line in lines:
            self.write(line)

    def __getattr__(self, name):
        return getattr(self._file, name)


def decode_pair(s, pos=0):
    """
    Decodes a name/value pair.

    The number of bytes decoded as well as the name/value pair
    are returned.
    """
    nameLength = ord(s[pos])
    if nameLength & 128:
        nameLength = struct.unpack('!L', s[pos:pos + 4])[0] & 0x7fffffff
        pos += 4
    else:
        pos += 1

    valueLength = ord(s[pos])
    if valueLength & 128:
        valueLength = struct.unpack('!L', s[pos:pos + 4])[0] & 0x7fffffff
        pos += 4
    else:
        pos += 1

    name = s[pos:pos + nameLength]
    pos += nameLength
    value = s[pos:pos + valueLength]
    pos += valueLength

    return pos, (name, value)


def encode_pair(name, value):
    """
    Encodes a name/value pair.

    The encoded string is returned.
    """
    nameLength = len(name)
    if nameLength < 128:
        s = chr(nameLength)
    else:
        s = struct.pack('!L', nameLength | 0x80000000L)

    valueLength = len(value)
    if valueLength < 128:
        s += chr(valueLength)
    else:
        s += struct.pack('!L', valueLength | 0x80000000L)

    return s + name + value


class Record(object):
    """
    A FastCGI Record.
    Used for encoding/decoding records.
    """

    def __init__(self, type=FCGI_UNKNOWN_TYPE, requestId=FCGI_NULL_REQUEST_ID):
        self.version = FCGI_VERSION_1
        self.type = type
        self.requestId = requestId
        self.contentLength = 0
        self.paddingLength = 0
        self.contentData = ''


    def _recvall(stream, length):
        """
        Attempts to receive length bytes from a socket, blocking if necessary.
        (Socket may be blocking or non-blocking.)
        """

        if FCGI_DEBUG: logging.debug('_recvall (%d)' % (length))

        dataList = []
        recvLen = 0

        while length:
            data = stream.read(length)
            if not data: # EOF
                break
            dataList.append(data)
            dataLen = len(data)
            recvLen += dataLen
            length -= dataLen

        #if FCGI_DEBUG: logging.debug('recived length = %d' % (recvLen))

        return ''.join(dataList), recvLen

    _recvall = staticmethod(_recvall)


    def read(self, stream):
        """Read and decode a Record from a socket."""
        try:
            header, length = self._recvall(stream, FCGI_HEADER_LEN)
        except:
            raise 
            raise EOFError

        if length < FCGI_HEADER_LEN:
            raise EOFError

        if FCGI_DEBUG:
            hex = ''
            for s in header:
                hex += '%x|' % (ord(s))

        self.version, self.type, self.requestId, self.contentLength,\
        self.paddingLength = struct.unpack(FCGI_Header, header)

        if FCGI_DEBUG: logging.debug('recv fcgi header: %s %s len: %d' % (FCGI_HEADER_NAMES[self.type] if self.type is not None and self.type < FCGI_MAXTYPE else FCGI_HEADER_NAMES[FCGI_MAXTYPE], hex, len(header)))

        if self.contentLength:
            try:
                self.contentData, length = self._recvall(stream, self.contentLength)
            except:
                raise EOFError

            if length < self.contentLength:
                raise EOFError

        if self.paddingLength:
            try:
                self._recvall(stream, self.paddingLength)
            except:
                raise EOFError

    def _sendall(stream, data):
        """
        Writes data to a socket and does not return until all the data is sent.
        """
        if FCGI_DEBUG: logging.debug('_sendall: len=%d' % len(data))
        stream.write(data)

    _sendall = staticmethod(_sendall)


    def write(self, stream):
        """Encode and write a Record to a socket."""
        if not self.contentLength:
            self.paddingLength = 8
        else:
            self.paddingLength = -self.contentLength & 7

        header = struct.pack(FCGI_Header, self.version, self.type,
                             self.requestId, self.contentLength,
                             self.paddingLength)

        if FCGI_DEBUG: logging.debug('send fcgi header: %s' % FCGI_HEADER_NAMES[self.type] if self.type is not None and self.type < FCGI_MAXTYPE else FCGI_HEADER_NAMES[FCGI_MAXTYPE])
        
        self._sendall(stream, header)

        if self.contentLength:
            if FCGI_DEBUG: logging.debug('send CONTENT')
            self._sendall(stream, self.contentData)
        if self.paddingLength:
            if FCGI_DEBUG: logging.debug('send PADDING')
            self._sendall(stream, '\x00' * self.paddingLength)



class Request(object):
    """
    Represents a single FastCGI request.

    These objects are passed to your handler and is the main interface
    between your handler and the fcgi module. The methods should not
    be called by your handler. However, server, params, stdin, stdout,
    stderr, and data are free for your handler's use.
    """

    def __init__(self, conn, inputStreamClass):
        self._conn = conn

        self.server = conn.server
        self.params = {}
        self.stdin = inputStreamClass(conn)
        self.stdout = OutputStream(conn, self, FCGI_STDOUT)
        self.stderr = OutputStream(conn, self, FCGI_STDERR)
        self.data = inputStreamClass(conn)


    def run(self):
        """Runs the handler, flushes the streams, and ends the request."""

        try:
            protocolStatus, appStatus = self.server.handler(self)
        except Exception, instance:
            if FCGI_DEBUG: 
                logging.error(traceback.format_exc())
            raise
            # TODO: fix it
            #self.stderr.flush()
            #if not self.stdout.dataWritten:
            #    self.server.error(self)
            #protocolStatus, appStatus = FCGI_REQUEST_COMPLETE, 0

        if FCGI_DEBUG: logging.debug('protocolStatus = %d, appStatus = %d' % (protocolStatus, appStatus))
        
        self._flush()
        self._end(appStatus, protocolStatus)


    def _end(self, appStatus=0L, protocolStatus=FCGI_REQUEST_COMPLETE):
        self._conn.end_request(self, appStatus, protocolStatus)


    def _flush(self):
        self.stdout.flush()
        self.stderr.flush()


class Connection(object):
    """
    A Connection with the web server.

    Each Connection is associated with a single socket (which is
    connected to the web server) and is responsible for handling all
    the FastCGI message processing for that socket.
    """

    _multiplexed = False
    _inputStreamClass = InputStream

    def __init__(self, stdin, stdout, server):
        self._stdin = stdin
        self._stdout = stdout
        self.server = server

        # Active Requests for this Connection, mapped by request ID.
        self._requests = {}


    def run(self):
        """Begin processing data from the socket."""

        self._keepGoing = True
        while self._keepGoing:
            try:
                self.process_input()
            except KeyboardInterrupt:
                break
            #except EOFError, inst:
            #    raise
            #    if FCGI_DEBUG: logging.error(str(inst))
            #    break


    def process_input(self):
        """Attempt to read a single Record from the socket and process it."""
        # Currently, any children Request threads notify this Connection
        # that it is no longer needed by closing the Connection's socket.
        # We need to put a timeout on select, otherwise we might get
        # stuck in it indefinitely... (I don't like this solution.)

        if not self._keepGoing:
            return

        rec = Record()
        rec.read(self._stdin)

        if rec.type == FCGI_GET_VALUES:
            self._do_get_values(rec)
        elif rec.type == FCGI_BEGIN_REQUEST:
            self._do_begin_request(rec)
        elif rec.type == FCGI_ABORT_REQUEST:
            self._do_abort_request(rec)
        elif rec.type == FCGI_PARAMS:
            self._do_params(rec)
        elif rec.type == FCGI_STDIN:
            self._do_stdin(rec)
        elif rec.type == FCGI_DATA:
            self._do_data(rec)
        elif rec.requestId == FCGI_NULL_REQUEST_ID:
            self._do_unknown_type(rec)
        else:
            # Need to complain about this.
            pass


    def writeRecord(self, rec):
        """
        Write a Record to the socket.
        """
        rec.write(self._stdout)


    def end_request(self, req, appStatus=0L, protocolStatus=FCGI_REQUEST_COMPLETE, remove=True):
        """
        End a Request.

        Called by Request objects. An FCGI_END_REQUEST Record is
        sent to the web server. If the web server no longer requires
        the connection, the socket is closed, thereby ending this
        Connection (run() returns).
        """

        # write empty packet to stdin
        rec = Record(FCGI_STDOUT, req.requestId)
        rec.contentData = ''
        rec.contentLength = 0
        self.writeRecord(rec)

        # write end request
        rec = Record(FCGI_END_REQUEST, req.requestId)
        rec.contentData = struct.pack(FCGI_EndRequestBody, appStatus,
                                      protocolStatus)
        rec.contentLength = FCGI_EndRequestBody_LEN
        self.writeRecord(rec)

        if remove:
            if FCGI_DEBUG: logging.debug('end_request: removing request from list')
            del self._requests[req.requestId]

        if FCGI_DEBUG: logging.debug('end_request: flags = %d' % req.flags)

        if not (req.flags & FCGI_KEEP_CONN) and not self._requests:
            if FCGI_DEBUG: logging.debug('end_request: set _keepGoing = False')
            self._keepGoing = False


    def _do_get_values(self, inrec):
        """Handle an FCGI_GET_VALUES request from the web server."""

        outrec = Record(FCGI_GET_VALUES_RESULT)

        pos = 0
        while pos < inrec.contentLength:
            pos, (name, value) = decode_pair(inrec.contentData, pos)
            cap = self.server.capability.get(name)
            if cap is not None:
                outrec.contentData += encode_pair(name, str(cap))

        outrec.contentLength = len(outrec.contentData)
        self.writeRecord(outrec)


    def _do_begin_request(self, inrec):
        """Handle an FCGI_BEGIN_REQUEST from the web server."""
        role, flags = struct.unpack(FCGI_BeginRequestBody, inrec.contentData)

        req = self.server.request_class(self, self._inputStreamClass)
        req.requestId, req.role, req.flags = inrec.requestId, role, flags
        req.aborted = False

        if not self._multiplexed and self._requests:
            # Can't multiplex requests.
            self.end_request(req, 0L, FCGI_CANT_MPX_CONN, remove=False)
        else:
            self._requests[inrec.requestId] = req


    def _do_abort_request(self, inrec):
        """
        Handle an FCGI_ABORT_REQUEST from the web server.

        We just mark a flag in the associated Request.
        """
        req = self._requests.get(inrec.requestId)
        if req is not None:
            req.aborted = True


    def _start_request(self, req):
        """Run the request."""
        # Not multiplexed, so run it inline.
        req.run()


    def _do_params(self, inrec):
        """
        Handle an FCGI_PARAMS Record.

        If the last FCGI_PARAMS Record is received, start the request.
        """

        req = self._requests.get(inrec.requestId)
        if req is not None:
            if inrec.contentLength:
                pos = 0
                while pos < inrec.contentLength:
                    pos, (name, value) = decode_pair(inrec.contentData, pos)
                    req.params[name] = value


    def _do_stdin(self, inrec):
        """Handle the FCGI_STDIN stream."""
        req = self._requests.get(inrec.requestId)

        if inrec.contentLength:
            if req is not None:
                req.stdin.add_data(inrec.contentData)
        else:
            self._start_request(req)


    def _do_data(self, inrec):
        """Handle the FCGI_DATA stream."""
        req = self._requests.get(inrec.requestId)
        if req is not None:
            req.data.add_data(inrec.contentData)


    def _do_unknown_type(self, inrec):
        """Handle an unknown request type. Respond accordingly."""
        outrec = Record(FCGI_UNKNOWN_TYPE)
        outrec.contentData = struct.pack(FCGI_UnknownTypeBody, inrec.type)
        outrec.contentLength = FCGI_UnknownTypeBody_LEN
        self.writeRecord(outrec)


class FCGIServer(object):
    request_class = Request
    maxwrite = 8192
    inputStreamShrinkThreshold = 102400 - 8192

    def __init__(self, application, environ=None,
                 multithreaded=False, multiprocess=False,
                 debug=False, roles=(FCGI_RESPONDER,),
                 app_root=None):
        if environ is None:
            environ = {}

        self.application = application
        self.environ = environ
        self.multithreaded = multithreaded
        self.multiprocess = multiprocess
        self.debug = debug
        self.roles = roles
        self._connectionClass = Connection
        self.capability = {
            # If threads aren't available, these are pretty much correct.
            FCGI_MAX_CONNS: 1,
            FCGI_MAX_REQS: 1,
            FCGI_MPXS_CONNS: 0
        }
        self.app_root = app_root


    def run(self):
        msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
        stdin = sys.stdin
        stdout = os.fdopen(sys.stdin.fileno(), 'w', 0)

        conn = Connection(stdin, stdout, self)
        conn.run()


    def handler(self, req):
        """Special handler for WSGI."""
        if req.role not in self.roles:
            return FCGI_UNKNOWN_ROLE, 0

        # Mostly taken from example CGI gateway.
        environ = req.params
        environ.update(self.environ)

        environ['wsgi.version'] = (1, 0)
        environ['wsgi.input'] = req.stdin
        stderr = TeeOutputStream((sys.stderr, req.stderr))
        environ['wsgi.errors'] = stderr
        environ['wsgi.multithread'] = False
        environ['wsgi.multiprocess'] = False
        environ['wsgi.run_once'] = False

        if environ.get('HTTPS', 'off') in ('on', '1'):
            environ['wsgi.url_scheme'] = 'https'
        else:
            environ['wsgi.url_scheme'] = 'http'

        self._sanitizeEnv(environ)

        headers_set = []
        headers_sent = []
        result = None

        def write(data):
            assert type(data) is str, 'write() argument must be string'
            assert headers_set, 'write() before start_response()'

            if not headers_sent:
                status, responseHeaders = headers_sent[:] = headers_set
                found = False
                for header, value in responseHeaders:
                    if header.lower() == 'content-length':
                        found = True
                        break
                if not found and result is not None:
                    try:
                        if len(result) == 1:
                            responseHeaders.append(('Content-Length',
                                                    str(len(data))))
                    except:
                        pass
                s = 'Status: %s\r\n' % status
                for header in responseHeaders:
                    s += '%s: %s\r\n' % header
                s += '\r\n'
                req.stdout.write(s)

            req.stdout.write(data)
            req.stdout.flush()

        def start_response(status, response_headers, exc_info=None):
            if exc_info:
                try:
                    if headers_sent:
                        # Re-raise if too late
                        raise exc_info[0], exc_info[1], exc_info[2]
                finally:
                    exc_info = None # avoid dangling circular ref
            else:
                assert not headers_set, 'Headers already set!'

            assert type(status) is str, 'Status must be a string'
            assert len(status) >= 4, 'Status must be at least 4 characters'
            assert int(status[:3]), 'Status must begin with 3-digit code'
            assert status[3] == ' ', 'Status must have a space after code'
            assert type(response_headers) is list, 'Headers must be a list'
            if FCGI_DEBUG:
                logging.debug('response headers:')
                for name, val in response_headers:
                    assert type(name) is str, 'Header name "%s" must be a string' % name
                    assert type(val) is str, 'Value of header "%s" must be a string' % name
                    logging.debug('%s: %s' % (name, val))

            headers_set[:] = [status, response_headers]
            return write

        try:
            try:
                result = self.application(environ, start_response)
                try:
                    for data in result:
                        if data:
                            write(data)
                    if not headers_sent:
                        write('') # in case body was empty
                finally:
                    #if hasattr(result, 'close'):
                    #    result.close()
                    pass
            #except socket.error, e:
            #    if e[0] != errno.EPIPE:
            #        raise # Don't let EPIPE propagate beyond server
            except:
                raise
        finally:
            pass

        return FCGI_REQUEST_COMPLETE, 0


    def _sanitizeEnv(self, environ):
        """Ensure certain values are present, if required by WSGI."""
        
        if FCGI_DEBUG:
            logging.debug('raw envs: {0}'.format(environ))

        #if not environ.has_key('SCRIPT_NAME'):
        #    environ['SCRIPT_NAME'] = ''
        # TODO: fix for django
        environ['SCRIPT_NAME'] = ''

        reqUri = None
        if environ.has_key('REQUEST_URI'):
            reqUri = environ['REQUEST_URI'].split('?', 1)

        if not environ.has_key('PATH_INFO') or not environ['PATH_INFO']:
            if reqUri is not None:
                environ['PATH_INFO'] = reqUri[0]
            else:
                environ['PATH_INFO'] = ''
        
        # convert %XX to python unicode
        environ['PATH_INFO'] = urllib.unquote(environ['PATH_INFO'])

        # process app_root
        if self.app_root and environ['PATH_INFO'].startswith(self.app_root):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.app_root):]

        if not environ.has_key('QUERY_STRING') or not environ['QUERY_STRING']:
            if reqUri is not None and len(reqUri) > 1:
                environ['QUERY_STRING'] = reqUri[1]
            else:
                environ['QUERY_STRING'] = ''

        # If any of these are missing, it probably signifies a broken
        # server...
        for name, default in [('REQUEST_METHOD', 'GET'),
                              ('SERVER_NAME', 'localhost'),
                              ('SERVER_PORT', '80'),
                              ('SERVER_PROTOCOL', 'HTTP/1.0')]:
            if not environ.has_key(name):
                environ['wsgi.errors'].write('%s: missing FastCGI param %s '
                                             'required by WSGI!\n' %
                                             (self.__class__.__name__, name))
                environ[name] = default


    def error(self, req):
        """
        Called by Request if an exception occurs within the handler. May and
        should be overridden.
        """
        if self.debug:
            import cgitb

            req.stdout.write('Status: 500 Internal Server Error\r\n' +
                             'Content-Type: text/html\r\n\r\n' +
                             cgitb.html(sys.exc_info()))
        else:
            errorpage = """<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>Unhandled Exception</title>
</head><body>
<h1>Unhandled Exception</h1>
<p>An unhandled exception was thrown by the application.</p>
</body></html>
"""
            req.stdout.write('Status: 500 Internal Server Error\r\n' +
                             'Content-Type: text/html\r\n\r\n' +
                             errorpage)


def example_application(environ, start_response):
    '''example wsgi app which outputs wsgi environment'''
    logging.debug('wsgi app started')
    data = ''
    env_keys = environ.keys()
    env_keys.sort()
    for e in env_keys:
        data += '%s: %s\n' % (e, environ[e])
    data += 'sys.version: '+sys.version+'\n'
    start_response('200 OK', [('Content-Type', 'text/plain'), ('Content-Length', str(len(data)))])
    yield data


def run_example_app():
    if FCGI_DEBUG: logging.info('run_fcgi: STARTED')
    FCGIServer(example_application).run()
    if FCGI_DEBUG: logging.info('run_fcgi: EXITED')


def run_django_app(django_settings_module, django_root):
    '''run django app by django_settings_module,
    django_settings_module can be python path or physical path
    '''
    if os.path.exists(django_settings_module):
        # this is physical path
        app_path, app_settings = os.path.split(django_settings_module)

        # add diretory to PYTHONPATH
        app_dir = os.path.dirname(app_path)
        if app_dir not in sys.path:
            sys.path.append(app_dir)
            if FCGI_DEBUG: logging.debug('%s added to PYTHONPATH' % app_dir)

        # cut .py extension in module
        if app_settings.endswith('.py'):
            app_settings = app_settings[:-3]

        # get python path to settings
        settings_module = '%s.%s' % (os.path.basename(app_path), app_settings)
    else:
        #consider that django_settings_module is valid python path
        settings_module = django_settings_module

    os.environ['DJANGO_SETTINGS_MODULE'] = settings_module
    if FCGI_DEBUG: logging.info('DJANGO_SETTINGS_MODULE set to %s' % settings_module)

    try:
        from django.core.handlers.wsgi import WSGIHandler
    except ImportError:
        if FCGI_DEBUG: logging.error('Could not import django.core.handlers.wsgi module. Check that django is installed and in PYTHONPATH.')
        raise



    FCGIServer(WSGIHandler(), app_root=django_root).run()

class Command(BaseCommand):
    args = '[root_path]'
    help = '''Run as a fcgi server'''
    def handle(self, *args, **options):
		django_root=args[0] if args else None
		if FCGI_LOG:
			logging.basicConfig(
				filename=os.path.join(FCGI_LOG_PATH, 'fcgi_%s_%d.log' %(datetime.datetime.now().strftime('%y%m%d_%H%M%S'), os.getpid())),
				filemode='w',
				format='%(asctime)s [%(levelname)-5s] %(message)s',
				level=logging.DEBUG)
		try:
			from django.core.handlers.wsgi import WSGIHandler
		except ImportError:
			if FCGI_DEBUG: logging.error('Could not import django.core.handlers.wsgi module. Check that django is installed and in PYTHONPATH.')
			raise



		FCGIServer(WSGIHandler(), app_root=django_root).run()


if __name__ == '__main__':

    # compile self
    compiled = os.path.split(__file__)[-1].replace('.py', '.pyc' if FCGI_DEBUG else '.pyo')
    if not os.path.exists(compiled):
        import py_compile
        try:
            py_compile.compile(__file__)
        except:
            pass

    # enable logging
    if FCGI_DEBUG:
        logging.basicConfig(
            filename=os.path.join(FCGI_LOG_PATH, 'fcgi_%s_%d.log' %(datetime.datetime.now().strftime('%y%m%d_%H%M%S'), os.getpid())),
            filemode='w',
            format='%(asctime)s [%(levelname)-5s] %(message)s',
            level=logging.DEBUG)
        
    # If we are inside a subdirectory of a django app, set the default Djan
    default_django_settings_module=None
    parent_settings_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'settings.py')
    if os.path.exists(parent_settings_file):
        default_django_settings_module = os.path.abspath(parent_settings_file)
        if FCGI_DEBUG: 
            logging.info('default DJANGO_SETTINGS_MODULE set to %s' % default_django_settings_module)


    # parse options
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("", "--django-settings-module", dest="django_settings_module", help="python or physical path to Django settings module")
    parser.add_option("", "--django-root", dest="django_root", help="strip this string from the front of any URLs before matching them against your URLconf patterns.")
    parser.set_defaults(
        django_settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', default_django_settings_module),
        django_root = os.environ.get('django.root', None)
    )

    (options, args) = parser.parse_args()

    # check django
    if options.django_settings_module:
        run_django_app(options.django_settings_module, options.django_root)
    else:
        # run example app
        run_example_app()

		


        