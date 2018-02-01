#!/usr/bin/env python
"""
Proxy an SSL connection to a Twisted endpoint based on the SNI extension

Allows for end-to-end encrypted connections from a browser to a Tor hidden
service.

Proxy code based on
http://blog.laplante.io/2013/08/a-basic-man-in-the-middle-proxy-with-twisted/

"""
import logging

from twisted.internet.endpoints import clientFromString
from twisted.internet import protocol, reactor
from OpenSSL import SSL

# Set up logging
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(fmt="%(asctime)s [%(levelname)s]: "
                                           "%(message)s"))
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(level=logging.DEBUG)


class NameResolver(object):
    """
    Resolve a domain to a Twisted client endpoint

    Takes a domain name and returns an endpoint. This demo uses a
    domain -> onion list. In future the resolver could query a TXT
    record from the domain to retrieve the destination TCP or onion address.
    """

    def __init__(self):
        # Testing domain list
        self.domain_list = {
            'oniontip.com': 'ha2zlm2uo6hnhdha',
            'blockchain.info': 'blockchainbdgpzk',
        }

    def resolve(self, domain):
        return self.domain_list.get(domain)

    def get_endpoint(self, domain):
        resolved_name = self.resolve(domain)

        if resolved_name:
            logger.info('Resolved domain %s to %s.onion',
                        domain, resolved_name)
            endpoint_string = 'tor:host={}.onion:port=443'.format(
                self.resolve(domain))

            try:
                endpoint = clientFromString(reactor, endpoint_string)
            except ValueError:
                logger.exception('Error creating client endpoint. Maybe a '
                                 'suitable endpoint parser is not available.')
                return None

            return endpoint
        else:
            logger.warn('Could not resolve domain %s.', domain)
            return None


class SSLContext(object):
    """
    Simple mocked SSL connection to allow parsing of the ClientHello
    """

    def __init__(self):
        """
        Initialize an SSL connection object
        """
        self.server_name = None

        context = SSL.Context(SSL.TLSv1_2_METHOD)
        context.set_tlsext_servername_callback(self.get_servername)

        self.connection = SSL.Connection(context=context)
        self.connection.set_accept_state()

    def get_servername(self, connection):
        """
        Callback to retrieve the parsed SNI extension when it is parsed
        """
        self.server_name = connection.get_servername()

    def parse_client_hello(self, client_hello):
        # Write the SSL handshake into the BIO memory stream.
        self.connection.bio_write(client_hello)
        try:
            # Start parsing the client handshake from the memory stream
            self.connection.do_handshake()
        except SSL.Error:
            # We don't have a complete SSL handshake, only the ClientHello,
            # close the connection once we hit an error.
            self.connection.shutdown()

        # Should have run the get_servername callback already
        return self.server_name


class ServerProtocol(protocol.Protocol):
    """
    Adapted from http://stackoverflow.com/a/15645169/221061
    """
    def __init__(self):
        self.buffer = None
        self.client = None
        self.resolve = NameResolver()

    def connectionMade(self):
        pass

    def parseSNI(self, data):
        ssl_context = SSLContext()
        return ssl_context.parse_client_hello(data)

    def createClient(self, endpoint):
        """
        Create an instance of the Client which connects to the
        destination server.
        """
        factory = protocol.ReconnectingClientFactory()
        factory.protocol = ClientProtocol
        factory.server = self

        # Connect client 'factory' to the destination
        logger.debug('Creating connection to endpoint.')
        d = endpoint.connect(factory)
        reactor.callLater(30, d.cancel)

    # Client => Proxy
    def dataReceived(self, data):
        if self.client:
            self.client.write(data)
        else:
            # Add ClientHello handshake into an outbound buffer
            self.buffer = data

            # Try to read the SNI header from the SSL ClientHello
            sni_domain = self.parseSNI(data)
            if sni_domain:
                logger.info('Got request with SNI %s.', sni_domain)

                # Resolve the domain to a Twisted client endpoint
                endpoint = self.resolve.get_endpoint(sni_domain)
                if endpoint:
                    self.createClient(endpoint)
                else:
                    # Could not resolve the SNI domain to an endpoint,
                    # close the user's connection to the proxy server.
                    self.transport.loseConnection()
            else:
                logger.warning("Got a request without SNI field, closing.")
                self.transport.loseConnection()

    # Proxy => Client
    def write(self, data):
        self.transport.write(data)


class ClientProtocol(protocol.Protocol):
    """
    Protocol for the connection to destination endpoint
    """

    def connectionMade(self):
        self.factory.server.client = self

        # Write the ClientHello from the buffer to the Client connection
        # when the connection is created
        self.write(self.factory.server.buffer)
        self.factory.server.buffer = None

        logger.debug('Connection to endpoint successful.')

    # Server => Proxy
    def dataReceived(self, data):
        self.factory.server.write(data)

    # Proxy => Server
    def write(self, data):
        if data:
            self.transport.write(data)

    def connectionLost(self, reason):
        logger.debug('Connection to endpoint lost.')
        # Close the proxy server connection when the client connection closes
        self.factory.server.transport.loseConnection()


def main():
    listening_port = 443
    factory = protocol.ServerFactory()
    factory.protocol = ServerProtocol

    # Start the proxy server listener
    logger.info("Starting SNI proxy server on port {}.".format(listening_port))
    reactor.listenTCP(listening_port, factory)
    reactor.run()


if __name__ == '__main__':
    main()