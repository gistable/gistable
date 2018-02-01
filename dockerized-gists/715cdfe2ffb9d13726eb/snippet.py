#!/usr/bin/env python

import sys, socket, thread, ssl
from select import select

HOST = '0.0.0.0'
PORT = 5222
BUFSIZE = 4096

# Change this with the first two bytes of the SSL client hello
SSL_CLIENT_HELLO_MARKER = '\x16\x03'
XMPP_SERVER = 'www.server.com'


def do_relay(client_sock, server_sock):
  server_sock.settimeout(1.0)
  client_sock.settimeout(1.0)
  print 'RELAYING'
  startTLSDone = 0
  while 1:
    try:

      receiving, _, _ = select([client_sock, server_sock], [], [])
      if client_sock in receiving:
        p = client_sock.recv(BUFSIZE)
        if len(p):
          print "C->S", len(p), repr(p)
        server_sock.send(p)

      if server_sock in receiving:
        p = server_sock.recv(BUFSIZE)
        if len(p):
          print "S->C", len(p), repr(p)

        if 'starttls' in p and not startTLSDone:
          # Strip StartTLS from the server's FEATURES
          p = p.replace("<starttls xmlns='urn:ietf:params:xml:ns:xmpp-tls'>"
            "</starttls>", '')
          p = p.replace("<starttls xmlns='urn:ietf:params:xml:ns:xmpp-tls'>"
            "<required/></starttls>", "")

          # Do startTLS handshake with the server
          print 'Wrapping server socket.'
          server_sock.send("<starttls xmlns='urn:ietf:params:xml:ns:xmpp-tls'/>")
          server_sock.recv(BUFSIZE)
          server_sock = ssl.wrap_socket(server_sock, suppress_ragged_eofs=True)

          # SSL handshake done; re-open the stream
          server_sock.send("<stream:stream to='" + XMPP_SERVER + "' "
            "xmlns:stream='http://etherx.jabber.org/streams' "
            "xmlns='jabber:client' xml:lang='en' version='1.0'>")

          # Receive the server's features
          server_sock.recv(BUFSIZE)
          startTLSDone = 1

        client_sock.send(p)

    except socket.error as e:
      if "timed out" not in str(e):
        raise e


def child(clientsock,target):
  targetsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  targetsock.connect((target,PORT))
  do_relay(clientsock, targetsock)

if __name__=='__main__':
  if len(sys.argv) < 4:
    sys.exit('Usage: %s TARGETHOST\n' % sys.argv[0])
  target = sys.argv[1]
  myserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  myserver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  myserver.bind((HOST, PORT))
  myserver.listen(2)
  print 'LISTENER ready on port', PORT
  while 1:
    client, addr = myserver.accept()
    print 'CLIENT CONNECT from:', addr
    thread.start_new_thread(child, (client,target))
