#!/usr/bin/python

"""
msysGit to Unix socket proxy
============================

This small script is intended to help use msysGit sockets with the new Windows Linux Subsystem (aka Bash for Windows).

It was specifically designed to pass SSH keys from the KeeAgent module of KeePass secret management application to the
ssh utility running in the WSL (it only works with Linux sockets). However, my guess is that it will have uses for other
applications as well.

In order to efficiently use it, I add it at the end of the ~/.bashrc file, like this:
    export SSH_AUTH_SOCK="/tmp/.ssh-auth-sock"
    ~/bin/msysgit2unix-socket.py /mnt/c/Users/User/keeagent.sock:$SSH_AUTH_SOCK

Command line usage: msysgit2unix-socket.py [-h] [--downstream-buffer-size N]
                                           [--upstream-buffer-size N] [--listen-backlog N]
                                           [--timeout N] [--pidfile FILE]
                                           source:destination [source:destination ...]

Positional arguments:
  source:destination    A pair of a source msysGit and a destination Unix
                        sockets.

Optional arguments:
  -h, --help            show this help message and exit
  --downstream-buffer-size N
                        Maximum number of bytes to read at a time from the
                        Unix socket.
  --upstream-buffer-size N
                        Maximum number of bytes to read at a time from the
                        msysGit socket.
  --listen-backlog N    Maximum number of simultaneous connections to the Unix
                        socket.
  --timeout N           Timeout.
  --pidfile FILE        Where to write the PID file.
"""

import argparse
import asyncore
import os
import re
import signal
import socket
import sys


class UpstreamHandler(asyncore.dispatcher_with_send):
    """
    This class handles the connection to the TCP socket listening on localhost that makes the msysGit socket.
    """
    def __init__(self, downstream_dispatcher, upstream_path):
        asyncore.dispatcher.__init__(self)
        self.out_buffer = b''
        self.downstream_dispatcher = downstream_dispatcher
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((b'localhost', UpstreamHandler.load_tcp_port_from_msysgit_socket_file(upstream_path)))

    @staticmethod
    def load_tcp_port_from_msysgit_socket_file(path):
        with open(path, 'r') as f:
            m = re.search(b'>([0-9]+)', f.readline())
            return int(m.group(1))

    def handle_connect(self):
        pass

    def handle_close(self):
        self.close()
        self.downstream_dispatcher.close()

    def handle_read(self):
        data = self.recv(config.upstream_buffer_size)
        if data:
            self.downstream_dispatcher.send(data)


class DownstreamHandler(asyncore.dispatcher_with_send):
    """
    This class handles the connections that are being accepted on the Unix socket.
    """
    def __init__(self, downstream_socket, upstream_path):
        asyncore.dispatcher.__init__(self, downstream_socket)
        self.out_buffer = b''
        self.upstream_dispatcher = UpstreamHandler(self, upstream_path)

    def handle_close(self):
        self.close()

    def handle_read(self):
        data = self.recv(config.downstream_buffer_size)
        if data:
            self.upstream_dispatcher.send(data)


class MSysGit2UnixSocketServer(asyncore.dispatcher):
    """
    This is the "server" listening for connections on the Unix socket.
    """
    def __init__(self, upstream_socket_path, unix_socket_path):
        asyncore.dispatcher.__init__(self)
        self.upstream_socket_path = upstream_socket_path
        self.create_socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.bind(unix_socket_path)
        self.listen(config.listen_backlog)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            DownstreamHandler(sock, self.upstream_socket_path)


def build_config():
    class ProxyAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            proxies = []
            for value in values:
                src_dst = value.partition(':')
                if src_dst[1] == b'':
                    raise parser.error(b'Unable to parse sockets proxy pair "%s".' % value)
                proxies.append([src_dst[0], src_dst[2]])
            setattr(namespace, self.dest, proxies)

    parser = argparse.ArgumentParser(
        description='Transforms msysGit compatible sockets to Unix sockets for the Windows Linux Subsystem.')
    parser.add_argument(b'--downstream-buffer-size', default=8192, type=int, metavar=b'N',
                        help=b'Maximum number of bytes to read at a time from the Unix socket.')
    parser.add_argument(b'--upstream-buffer-size', default=8192, type=int, metavar=b'N',
                        help=b'Maximum number of bytes to read at a time from the msysGit socket.')
    parser.add_argument(b'--listen-backlog', default=100, type=int, metavar=b'N',
                        help=b'Maximum number of simultaneous connections to the Unix socket.')
    parser.add_argument(b'--timeout', default=60, type=int, help=b'Timeout.', metavar=b'N')
    parser.add_argument(b'--pidfile', default=b'/tmp/msysgit2unix-socket.pid', metavar=b'FILE',
                        help=b'Where to write the PID file.')
    parser.add_argument(b'proxies', nargs=b'+', action=ProxyAction, metavar='source:destination',
                        help=b'A pair of a source msysGit and a destination Unix sockets.')
    return parser.parse_args()


def daemonize():
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit()
    except OSError:
        sys.stderr.write(b'Fork #1 failed.')
        sys.exit(1)

    os.chdir(b'/')
    os.setsid()
    os.umask(0)

    try:
        pid = os.fork()
        if pid > 0:
            sys.exit()
    except OSError:
        sys.stderr.write(b'Fork #2 failed.')
        sys.exit(1)

    sys.stdout.flush()
    sys.stderr.flush()

    si = open('/dev/null', 'r')
    so = open('/dev/null', 'a+')
    se = open('/dev/null', 'a+')
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

    pid = str(os.getpid())
    with open(config.pidfile, 'w+') as f:
        f.write(b'%s\n' % pid)


def cleanup():
    for pair in config.proxies:
        os.remove(pair[1])
    os.remove(config.pidfile)
    sys.exit(0)


if __name__ == b'__main__':
    config = build_config()

    if os.path.exists(config.pidfile):
        sys.stderr.write(
            b'%s: Already running (or at least pidfile "%s" already exists).\n' % (sys.argv[0], config.pidfile))
        sys.exit(0)

    for pair in config.proxies:
        MSysGit2UnixSocketServer(pair[0], pair[1])

    daemonize()
    signal.signal(signal.SIGTERM, cleanup)

    asyncore.loop(config.timeout, True)
    