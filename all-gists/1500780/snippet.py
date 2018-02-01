#!/usr/bin/env python

"""
This works for me, but as always, YMMV

There are little things still @todo for the command line
but the class should be enough to do everything you need

basic localhost usage: ./cgminer-rpc <command>
"""

import socket
import sys

try:
    import json
except ImportError:
    import simplejson as json

class CgminerClient:
    """
    With help from runeks and http://docs.python.org/howto/sockets.html
    """

    def command(self, host, port, command):
	# sockets are one time use. open one for each command
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # connect to the given host and port
            sock.connect((host, port))

            # json encode and send the command
            self._send(sock, json.dumps({"command": command}))

            # receive any returned data
            received = self._receive(sock)
        finally:
            # shutdown and close the socket properly
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
        
        # the null byte makes json decoding unhappy
        decoded = json.loads(received.replace('\x00', ''))

        return decoded

    def _send(self, sock, msg):
        totalsent = 0
        while totalsent < len(msg):
            sent = sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    def _receive(self, sock, size=65500):
        msg = ''
        while True:
            chunk = sock.recv(size)
            if chunk == '':
                # end of message
                break
            msg = msg + chunk
        return msg

if __name__ == "__main__":
    # @todo use argparse
    # @todo take a hostname and port from command line
    command = sys.argv[1]

    # @todo use real logging
    print command

    client = CgminerClient()

    # send command and print the response
    print client.command('localhost', 4028, command)

