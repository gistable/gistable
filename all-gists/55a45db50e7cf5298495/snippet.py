"""
SSL/TLS negotiation.
"""

import asyncore
import logging
import socket
import ssl


logger = logging.getLogger(__name__)


class TLSHandshake(asyncore.dispatcher):
    """
    Negotiates a SSL/TLS connection before handing itself spawning a
    dispatcher that can deal with the overlying protocol as soon as the
    handshake has been completed.

    `handoff` is a function/method called when the handshake has completed.
    `address` is a tuple consisting of hostname/address and port to connect to
    if nothing is passed in `sock`, which can take an already-connected socket.
    `certfile` can take a path to a certificate bundle, and `server_side`
    indicates whether the socket is intended to be a server-side or client-side
    socket.
    """

    want_read = want_write = True

    def __init__(self, handoff, address=None, sock=None,
                 certfile=None, server_side=False):
        asyncore.dispatcher.__init__(self, sock)
        self.certfile = certfile
        self.server_side = server_side
        self.handoff = handoff
        if sock is None:
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            logger.info('Connecting to %s%d', address[0], address[1])
            self.connect(address)
        elif self.connected:
            # Initiate the handshake for an already-connected socket.
            self.handle_connect()

    def handle_connect(self):
        # Once the connection has been established, it's safe to wrap the
        # socket.
        self.socket = ssl.wrap_socket(self.socket,
                                      server_side=self.server_side,
                                      ssl_version=ssl.PROTOCOL_TLSv1,
                                      certfile=self.certfile,
                                      keyfile=self.certfile,
                                      do_handshake_on_connect=False)

    def writable(self):
        return self.want_write

    def readable(self):
        return self.want_read

    def _handshake(self):
        """
        Perform the handshake.
        """
        try:
            self.socket.do_handshake()
        except ssl.SSLError, err:
            self.want_read = self.want_write = False
            if err.args[0] == ssl.SSL_ERROR_WANT_READ:
                self.want_read = True
            elif err.args[0] == ssl.SSL_ERROR_WANT_WRITE:
                self.want_write = True
            else:
                raise
        else:
            # The handshake has completed, so remove this channel and...
            self.del_channel()
            # ...hand the socket off to another channel now that the handshake
            # has completed.
            self.handoff(self.socket)

    handle_read = handle_write = _handshake