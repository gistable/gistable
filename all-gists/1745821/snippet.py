#!/usr/bin/env python

import sys
import socket
import xmlrpclib
import argparse


def supervisord_processes(address):
    try:
        server = xmlrpclib.Server(address)
        return server.supervisor.getAllProcessInfo()
    except socket.error:  # supervisord is down
        return None
    except xmlrpclib.ProtocolError:  # auth failed
        return None


def ok(message):
    sys.stdout.write('OK: %s' % message)
    sys.exit(0)


def warning(message):
    sys.stdout.write('WARNING: %s' % message)
    sys.exit(1)


def critical(message):
    sys.stdout.write('CRITICAL: %s' % message)
    sys.exit(2)


def main():
    parser = argparse.ArgumentParser(
        description='Monit script for supervisord.')
    parser.add_argument('address', type=str, help='supervisord address')
    args = parser.parse_args()

    pl = supervisord_processes(args.address)
    if not pl:
        critical('Can not get processes.')

    checked_names = []
    for p in pl:
        if p['state'] != 20:
            critical(
                'Process %s has state=%s (expected 20).' %
                (p['name'], p['state']))
        checked_names.append(p['name'])

    ok(', '.join(checked_names))


if __name__ == '__main__':
    main()
