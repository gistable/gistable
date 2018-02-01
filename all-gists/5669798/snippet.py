from itertools import chain
import multiprocessing
import socket
import sys


def static_view(env, start_response):
    mes = 'test'
    start_response('200 OK', [('Cache-Control', 'private'),
                   ('Content-Type', 'text/html'),
                   ('Connection', 'Close')])
    return mes


class BadRequest(Exception):
    pass


def handle_badrequest():
    return ['400 Bad Request']


class GaramServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET,
                                    socket.SOCK_STREAM)

    def bind_socket(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))

    def handle(self, data):
        return []

    def _serve(self, conn, addr):
        data = conn.recv(1024)
        try:
            mes = self.handle(data)
        except BadRequest:
            mes = handle_badrequest()

        for m in mes:
            conn.send(m)

    def serve(self):
        self.bind_socket()
        self.socket.listen(1)
        while True:
            try:
                conn, addr = self.socket.accept()
                process = multiprocessing.Process(target=self._serve, args=(conn, addr))
                process.daemon = True
                process.start()
                conn.close()
            except Exception:
                for process in multiprocessing.active_children():
                    process.terminate()
                    process.join()
                break


class WSGIRequestParser(object):
    def __init__(self, data):
        self.data = data
        self.head = data.split('\n\n')[0]
        self.body = ''

    def parse_head(self, head):
        env = {}
        head = head.split('\n')
        try:
            env['METHOD'], env['URI'], env['VERSION'] = head[0].split()
        except ValueError:
            raise BadRequest
        for h in head[1:]:
            if ': ' in h:
                k, v = h.split(': ')
                env[k] = v
        return env

    def parse(self):
        env = self.parse_head(self.head)
        return env


class WSGIResponseParser(object):
    def __init__(self, status, headers, body):
        self.status = status
        self.headers = headers
        self.body = body

    def parse_header(self, status, headers):
        header_strs = []
        header_strs.append('HTTP/1.0 %s' % status)
        header_strs.extend(['%s: %s' % (k, v) for k, v in headers])
        return '\n'.join(header_strs)

    def parse(self):
        parsed_header = self.parse_header(self.status, self.headers)
        res = chain([parsed_header, '\n\n'], self.body)
        return res


class GaramWSGIServer(GaramServer):
    def __init__(self, app,
                 host='127.0.0.1',
                 port=8000,
                 RequestParser=WSGIRequestParser,
                 ResponseParser=WSGIResponseParser):
        self.app = app
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET,
                                    socket.SOCK_STREAM)
        self.RequestParser = RequestParser
        self.ResponseParser = ResponseParser

    def start_response(self, status, headers):
        self.status, self.headers = status, headers

    def handle(self, data):
        request_parser = self.RequestParser(data)
        environ = request_parser.parse()
        body = self.app(environ, self.start_response)
        response_parser = self.ResponseParser(self.status,
                                              self.headers,
                                              body)
        response = response_parser.parse()
        return response

if __name__ == '__main__':
    server = GaramWSGIServer(static_view)
    server.serve()
