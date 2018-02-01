#!/usr/bin/env python3
"""Show server's certificate as json.

Usage:
  $ %(prog)s HOST [PORT]
"""
import json
import socket
import ssl
import sys

def getcert(addr, timeout=None):
    """Retrieve server's certificate at the specified address (host, port)."""
    # it is similar to ssl.get_server_certificate() but it returns a dict
    # and it verifies ssl unconditionally, assuming create_default_context does
    with socket.create_connection(addr, timeout=timeout) as sock:
        context = ssl.create_default_context()
        with context.wrap_socket(sock, server_hostname=addr[0]) as sslsock:
            return sslsock.getpeercert()

def main(argv):
    host = argv[1]
    port = int(argv[2]) if len(argv) > 2 else 443
    print(json.dumps(getcert((host, port)), indent=2, sort_keys=True))

if __name__ == "__main__":
    main(sys.argv)
