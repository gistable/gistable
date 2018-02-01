#!/usr/bin/python

import logging
import optparse
import sys
import socket
# 3 seconds timeout
_SOCKET_TIMEOUT = 3

class KestrelClient:
    """Very basic client"""

    def __init__(self, servers, port):
        """Derp"""
        self.servers = servers
        self.port = port
        self.set_servers(servers)

    def disconnect_all(self):
        for server in self.servers:
            server.close_socket()

    def set_servers(self, servers):
        self.servers = [Host(host, self.port) for host in self.servers]

    def send_cmd(self, cmd):
        res = {}
        for host in self.servers:
            logging.debug('[send-cmd] %s => %s', host.host, cmd)
            host.send_cmd(cmd)
            readline = host.readline
            server_data = {}
            while 1:
                line = readline()
                if not line or line.strip() == 'END':
                    break
                print line
        logging.debug(res)
        return res

class Host:

    def __init__(self, host, port, socket_timeout=_SOCKET_TIMEOUT):
        self.host = host
        self.port = port
        self.socket_timeout = socket_timeout
        self.socket = None
        self.buffer = ''
        self.connect()

    def connect(self):
        if self._get_socket():
            return True
        return False
    
    def _get_socket(self):
        if self.socket:
            return self.socket

        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if hasattr(conn, 'settimeout'):
            conn.settimeout(self.socket_timeout)

        try:
            logging.debug(self.host)
            conn.connect((self.host, self.port))
        except socket.timeout, msg:
            logging.info('[conn-error] %s', self.host)
            self.socket.close()
            self.socket = None

        self.socket = conn
        self.buffer = ''
        return conn

    def send_cmd(self, cmd):
        self.socket.send(cmd + '\r\n')

    def readline(self):
        buf = self.buffer
        recv = self.socket.recv
        while True:
            index = buf.find('\r\n')
            if index >= 0:
                break
            data = recv(4096)
            if not data:
                # connection close, let's kill it and raise
                self.close_socket()
                raise _ConnectionDeadError()

            buf += data
        self.buffer = buf[index+2:]
        return buf[:index]


def main():
    options = parse_args(sys.argv)

    kestrel_hosts = options.kestrel_hosts.split(',')
    logging.info('Connecting to hosts')
    client = KestrelClient(kestrel_hosts, options.port)
    while True:
        command = raw_input('> ')
        client.send_cmd(command)


def parse_args(argv):
    """Parses ars from sys"""
    p = optparse.OptionParser(usage='%prog [OPTIONS]', description=__doc__)
    p.add_option('--port', dest='port', type='int', default=22133)
    p.add_option('--kestrel-hosts', dest='kestrel_hosts', default=None,
        help='Comma separated list of hostnames.')
    p.add_option('-v', '--verbose', dest='verbose', action='store_true',
        default=False)
    options, args = p.parse_args(argv)
    if len(args) > 1:
        p.error('Unexpected argument: %s' % ', '.join(args[1:]))

    for opt in p.option_list:
        if opt.dest:
            if getattr(options, opt.dest) is None:
                p.error('%s is required!' % opt.get_opt_string())
    logger = logging.getLogger()
    logger.setLevel(options.verbose and logging.DEBUG or logging.INFO)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(
        logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s'))
    logger.addHandler(stream_handler)
    return options


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.error('Ctrl-C: Quitting early')