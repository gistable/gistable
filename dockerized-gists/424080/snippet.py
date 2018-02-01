#!/usr/bin/env python
#
# pyget2.py
# A python download accelerator
#
# This file uses multiprocessing along with
# chunked/parallel downloading to speed up
# the download of files (if possible).
#
# @author  Benjamin Hutchins
# @project Lead Bulb Download Manager
#
# Copyright 2010 Benjamin Hutchins
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import sys
import time
import urlparse
import cgi
import socket
import cookielib
import urllib2
import ftplib
import multiprocessing



# Set static variables
byte_size = 1024 * 8  # This is the byte memory cache size, increase this to use more memory and less disk writes
first_connection = None # This will have to be changed soon
chunked_conns = 4 # number of parallel connections to maintain


def write(text):
    '''Write and then flush, useful for multi-process'''
    print text
    sys.stdout.flush()


def log(text, lock = None):
    '''Log events for debugging and to see what broke later on'''
    if lock: lock.acquire(block=True, timeout=None)
    write(text)
    if lock: lock.release()


def kill(text):
    '''Print a message and kill the program'''
    print '%s: %s' % (__file__, text)
    sys.exit(1)


class Header(str):
    '''This is a custom String Object,
    used to manipulate HTTP Header returns'''
    pass


class Connection:
    '''Connection handles a single connection to the
    server hosting the download file.'''

    def __init__(self, handler):
        self.handler = handler
        self.ftp = False

        self.parse = self.handler.parse
        self.uri = self.handler.uri


    def connect(self, start = 0, end = 0):
        '''Connect to server that hosts the file user
        wishes to download.

        start is the byte to start the download at.'''

        uri = self.uri
        parse = self.parse
        ret = False


        log('Connecting... (url: %s)' % uri)


        # FTP and FTPS
        if parse.scheme in ('ftp', 'ftps', ):
            self.ftp = True
            self.ftp = ftplib.FTP()

            if parse.port:  self.ftp.connect( parse.hostname, parse.port )
            else:           self.ftp.connect( parse.hostname )

            if parse.username and parse.password:
                log('\tTrying User: %s\n\tPass: %s' % (parse.username, parse.password))
                self.ftp.login( parse.username, parse.password )
            else:
                log('\tTrying Anonymous FTP Login')
                self.ftp.login()

            log('\tChanging working directory..')
            self.ftp.cwd( os.path.dirname(parse.path) )

            try:
                self.conn = self.ftp.transfercmd('RETR %s' % os.path.basename(parse.path), start)
                ret = True
            except ftplib.error_reply:
                self.conn = self.ftp.transfercmd('RETR %s' % os.path.basename(parse.path))
                ret = False


        # HTTP and HTTPS
        elif parse.scheme in ('http', 'https', ):

            # Make Request
            request = urllib2.Request(uri)

            if start > 0:
                request.add_header('Range', 'bytes=%i-%i' % (start, end))

            # Handle Basic Authentication
            if parse.username and parse.password:
                passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
                passman.add_password(None, parse.geturl(), parse.username, parse.password)
                authhandler = urllib2.HTTPBasicAuthHandler(passman)
                opener = urllib2.build_opener(authhandler)

                log('\tTrying User: %s\n\tPass: %s' % (parse.username, parse.password))
                self.conn = opener.open(request)
            else:
                self.conn = urllib2.urlopen(request)

            # Look for redirected download
            uri = str(self.conn.geturl())
            if len(uri):
                self.handler.uri = uri # update so we can try and connect directly

            # Read needed headers
            if self.headers.get('Accept-Ranges', False):
                ret = True
            else:
                ret = False


        # Unsupported Scheme
        else:
            kill('Unsupported scheme!')


        if ret: log('\tResume supported :-)')
        else:   log('\tResume not supported :-(')

        return ret


    @property
    def filesize(self):
        '''Wrapper to get filesize sent by server'''
        if self.ftp:    filesize = self.ftp.size(os.path.basename(self.parse.path))
        else:           filesize = self.headers.get('Content-Length', None)

        if filesize is not None:
            return int(str(filesize)) # go to str first for headers
        else:
            return None


    @property
    def filename(self):
        '''Wrapper to get filename sent by server'''
        filename = self.headers.get('Content-Disposition', False)
        if filename: filename = filename.filename
        if not filename: filename = os.path.basename(self.handler.parse.path)
        return filename


    @property
    def headers(self):
        '''Wrapper to parse headers'''
        if self.ftp or hasattr(self, 'conn') is False:
            return {}

        headers = {}
        for header in str(self.conn.info()).split('\n'):
            if ':' in header:
                # Find header name
                parts = header.split(':')
                name = parts.pop(0).strip()
                value = ':'.join(parts).strip()

                # Turn value into a custom str object
                value = Header(value)

                # Assign extras
                (junk, parts) = cgi.parse_header(header)
                for key in parts.keys():
                    setattr(value, key, parts[key])

                # Add header to dict
                headers[name] = value

        return headers


    def read(self, bytes = None):
        '''Wrapper to read more data from connection'''
        if self.ftp:
            if bytes:   return self.conn.recv(bytes)
            else:       return self.conn.recv()
        else:
            if bytes:   return self.conn.read(bytes)
            else:       return self.conn.read()


    def close(self):
        '''Wrapper to close the connection'''
        try:
            self.conn.close()
        except:
            pass



class Handler:

    def __init__(self, uri):

        # Parse URI
        self.uri = url
        self.parse = urlparse.urlparse(self.uri)
        self.dir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))


        # Gather fileinfo from Request
        self.gather()


    def gather(self):
        connection = Connection(self)
        self.can_resume = connection.connect()

        self.filesize = connection.filesize
        self.filename = connection.filename
        download = True


        # To chunk we need Resume-capability
        #  and to know the Filesize
        if self.can_resume and self.filename:
            # Confirm number of connections
            #  is greater than one
            if chunked_conns > 1:
                global first_connection
                first_connection = connection
                chunks = self.chunk(chunked_conns)
                self.start(chunks)

                if not self.rebuild():
                    log('Download is apparently not done!')
                    return

                download = False


        # We weren't able to chunk, continue
        #  download through open connection
        if download:
            savepath = os.path.join(self.dir, self.filename)
            log('Downloading with single connection to %s' % savepath)
            print str(connection.headers)
            output_file = open(savepath, 'wb')

            while 1:
                chunk = connection.read(byte_size)
                if not chunk: # EOF
                    break
                output_file.write(chunk)

            output_file.close()
            connection.close()


        # Update Status
        log('Download complete')


    def chunk(self, chunked_conns):
        '''Divide the file into chunk sizes
        to download.'''

        chunks = [] # chunks
        handled = 0 # to confirm every byte is accounted for


        # Look to resume the download
        files = os.listdir(self.dir)
        if files:
            chunked_conns = 0
            for filename in files:
                if '.part' in filename:
                    # Get info from file
                    parts = filename.split('.')
                    (start, end, bytes) = (int(parts[0]), int(parts[1]), int(os.path.getsize(os.path.join(self.dir, filename))))

                    # Change start to start where this download ended
                    start = start + bytes

                    # Change bytes to be updated
                    bytes = end - start

                    if bytes > 0:

                        # Add new Chunk
                        chunks.append((chunked_conns, start, end, bytes, filename))

                        # Increment number of chunks
                        chunked_conns = chunked_conns + 1


        # Chunk up size
        else:
            per_conn = int(self.filesize / chunked_conns)
            for i in range(0, chunked_conns):
                filename = '%i.%i.part' % (handled, handled + per_conn)
                chunks.append((
                    i,                      # number
                    handled,                # start
                    handled + per_conn,     # end
                    per_conn,               # number of bytes
                    filename,               # file to write to
                    ))
                handled = handled + per_conn


            # check difference of handled
            diff = self.filesize - handled
            if diff > 0:
                (i, start, end, bytes, filename) = chunks.pop()
                end = end + diff
                bytes = bytes + diff
                filename = '%i.%i.part' % (start, end)
                chunks.append((i, start, end, bytes, filename))
            elif diff < 0:
                (i, start, end, bytes, filename) = chunks.pop()
                end = end - diff
                bytes = bytes - diff
                filename = '%i.%i.part' % (start, end)
                chunks.append((i, start, end, bytes, filename))

        return chunks


    def start(self, chunks):
        '''Start subprocesses for each chunk connection'''
        ps = []
        lock = multiprocessing.Lock()

        # Start connections
        for chunk in chunks:
            p = multiprocessing.Process(target=self.connect, args=chunk + (lock,))
            p.start()
            ps.append(p)

        # Wait for all to finish
        for p in ps:
            p.join()


    def connect(self, number, start, end, totalbytes, filename, lock):
        '''Connect to server, download this chunk

        number      connection number
        connection  active connection, can be None
                        if None must open a connection
        start       first byte to get
        end         last byte to get
        totalbytes  total amount of bytes to download'''

        # Start a timer
        tic = time.time()
        log('connection %i: started (time now is %i)' % (number, tic), lock)


        # Start a connection
        global first_connection
        if number == 0 and first_connection:
            connection = first_connection
        else:
            connection = Connection(self)
            connection.connect(start, end-1) # -1 on end HTTP 1.1


        # Check filesize
        size = connection.filesize
        if not size:
            log('connection %i: filesize was not returned' % number, lock)
            return

        if self.filesize != size and totalbytes != size:
            log('connection %i: received different filesize, killing this connection (got: %i, wanted %i or %i)' % (number, size, self.filesize, totalbytes), lock)
            return


        # Start file
        filename = os.path.join(self.dir, filename)
        if os.path.exists(filename):    filepart = open(filename, 'ab')
        else:                           filepart = open(filename, 'wb')
        fetched = 0 # number of bytes downloaded through this connection


        # Start Downloading
        log('connection %i: receiving data (want to get %i)' % (number, totalbytes))
        while totalbytes > fetched:
            # Determine amount of bytes to get
            bytes = byte_size

            # Should we only get remaining bytes?
            if fetched + bytes > totalbytes:
                bytes = totalbytes - fetched

            # Grab the chunk
            #log('connection %i: getting %i bytes' % (number, bytes), lock)
            chunk = connection.read(bytes)

            # Write the chunk to file
            filepart.write(chunk)

            # Continue
            fetched = fetched + len(chunk)


        # Close stuff
        log('connection %i: closing connection and part file' % number, lock)
        connection.close()  # close the connection
        filepart.close()    # close the file


        # Finish timer
        toc = time.time()
        t = toc-tic
        log('connection %i: time %i, average speed %f bps, downloaded %i bytes' % (number, t, float(fetched / t), fetched), lock)


    def rebuild(self):

        # Get list of part files
        files = os.listdir(self.dir)
        files.sort() # sort in order to make sure we append properly

        # Confirm file sizes, make sure we have all data
        bytes = 0
        for filename in files:
            if '.part' in filename:
                file = os.path.join(self.dir, filename)
                filesize = int(os.path.getsize(file))
                bytes = bytes + filesize

                (start, end, ext) = filename.split('.')
                total = int(end) - int(start)
                log('Part File: %s, should be %s, is %i, needs %i' % (filename, total, filesize, total - filesize))


        if bytes != self.filesize:
            log('Filesizes do not match! Something went wrong!')
            return False


        # Create output file
        path = os.path.join(self.dir, self.filename)
        log('Rebuilding file to %s' % path)
        output_file = open(path, 'wb')


        # Rebuild file
        for filename in files:
            if '.part' in filename:
                # Open part file
                f = os.path.join(self.dir, filename)
                file = open(f, 'rb')

                # Write contents to output file
                output_file.write(file.read()) # TODO: make this go through a "while" to have a percentage bar

                # Close file part, so we can delete it (not-in-use)
                file.close()

                # Delete part file
                os.remove(f)


        # Close output file
        output_file.close()
        return True


def main(argv):
    if len(argv) != 2:
        kill('Must pass a URL to download')

    print 'Starting download of file ' + argv[1]

    Handler(arv[1])



if __name__ == '__main__':
	main(sys.argv)