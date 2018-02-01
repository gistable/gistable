#!/usr/bin/env python
#
# When triggered via a HTTP request, execute a command.
#
# Written by Senko Rasic <senko.rasic@goodcode.io>
# Released into Public Domain. Use it as you like.
#
# Usage: python trigger.py <host> <port> <key> <command>...
#
# HTTP GET and POST requests are supported. If you need more verbs or need
# to disable one of the two, edit the script. The request should have a
# "key" argument (via query string if GET, or body (urlencoded form) if POST),
# and the trigger is only activated if the key matches what's given on the
# command line.
#
# The command given on the commandline is executed (along with any arguments
# if given). If the command exits successfully (exit status 0), HTTP response
# code 200 is returned to the user, otherwise 500 is returned.
#
# Host is usually 0.0.0.0 (unless you want to listen only on a specific
# address/interface), port is the TCP port to listen on, key is the key
# that the client will have to supply to authorize the trigger, and the
# command is what should be executed.


from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from urlparse import urlparse, parse_qs
from subprocess import call
import sys


class RequestHandler(BaseHTTPRequestHandler):
    key = None
    command = []

    def _parse_request(self):
        parsed_req = urlparse(self.path)
        args = parse_qs(parsed_req.query)
        if self.headers.get('content-type', '') \
            == 'application/x-www-form-urlencoded':
                body = self.rfile.read(int(self.headers.get('content-length')))
                args = parse_qs(body)

        args = dict((k, v[0]) for k, v in args.iteritems())
        return (parsed_req.path, args)

    def do_POST(self):
        path, args = self._parse_request()
        self.do('POST', path, args)

    def do_GET(self):
        path, args = self._parse_request()
        self.do('GET', path, args)

    def do(self, method, path, args):
        if args.get('key') != RequestHandler.key:
            self.send_error(400, 'Bad Request')
            return

        try:
            retval = call(RequestHandler.command)
        except OSError:
            retval = -1

        if retval == 0:
            self.send_response(200)
            self.end_headers()
        else:
            self.send_error(500, 'Trigger command failed')


def run(host, port, key, *command):
    RequestHandler.key = key
    RequestHandler.command = command

    server = HTTPServer((host, port), RequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    if len(sys.argv) < 5:
        sys.stderr.write('Usage: %s <host> <port> <key> <cmd> ...\n' %
            sys.argv[0])
        sys.exit(-1)
    run(sys.argv[1], int(sys.argv[2]), sys.argv[3], *sys.argv[4:])
    sys.exit(0)
