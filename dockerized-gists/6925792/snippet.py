#!/usr/bin/env python
# -*- coding: utf-8 -*-

import calendar
import sys

import rdbtools


def emit_protocol(*args):
    """Emit Redis unified protocol.
    """
    sys.stdout.write(u"*" + unicode(len(args)) + u"\r\n")
    for arg in args:
        sys.stdout.write(u"$" + unicode(len(unicode(arg))) + u"\r\n")
        sys.stdout.write(unicode(arg) + u"\r\n")


def unix_timestamp(dt):
     return calendar.timegm(dt.utctimetuple())


class ProtocolCallback(rdbtools.RdbCallback):
    def __init__(self):
        self.reset()

    def reset(self):
        self._expires = {}

    def set_expiry(self, key, dt):
        self._expires[key] = dt

    def get_expiry_seconds(self, key):
        if key in self._expires:
            return unix_timestamp(self._expires[key])
        return None

    def expires(self, key):
        return key in self._expires

    def pre_expiry(self, key, expiry):
        if expiry is not None:
            self.set_expiry(key, expiry)

    def post_expiry(self, key):
        if self.expires(key):
            self.expireat(key, self.get_expiry_seconds(key))

    def start_database(self, db_number):
        self.reset()
        self.select(db_number)

    # String handling

    def set(self, key, value, expiry, info):
        self.pre_expiry(key, expiry)
        emit_protocol('SET', key, value)
        self.post_expiry(key)

    # Hash handling

    def start_hash(self, key, length, expiry, info):
        self.pre_expiry(key, expiry)

    def hset(self, key, field, value):
        emit_protocol('HSET', key, field, value)

    def end_hash(self, key):
        self.post_expiry(key)

    # Set handling

    def start_set(self, key, cardinality, expiry, info):
        self.pre_expiry(key, expiry)

    def sadd(self, key, member):
        emit_protocol('SADD', key, member)

    def end_set(self, key):
        self.post_expiry(key)

    # List handling

    def start_list(self, key, length, expiry, info):
        self.pre_expiry(key, expiry)

    def rpush(self, key, value):
        emit_protocol('RPUSH', key, value)

    def end_list(self, key):
        self.post_expiry(key)

    # Sorted set handling

    def start_sorted_set(self, key, length, expiry, info):
        self.pre_expiry(key, expiry)

    def zadd(self, key, score, member):
        emit_protocol('ZADD', key, score, member)

    def end_sorted_set(self, key):
        self.post_expiry(key)

    # Other misc commands

    def select(self, db_number):
        emit_protocol('SELECT', db_number)

    def expireat(self, key, timestamp):
        emit_protocol('EXPIREAT', key, timestamp)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--db', dest='dbs', action='append', type=int)
    parser.add_argument('-t', '--type', dest='types', action='append')
    parser.add_argument('-k', '--key', dest='keys')
    parser.add_argument('rdbfile')
    args = parser.parse_args()

    filters = {}
    if args.dbs:
        filters['dbs'] = args.dbs
    if args.types:
        filters['types'] = args.types
    if args.keys:
        filters['keys'] = args.keys

    callback = ProtocolCallback()
    parser = rdbtools.RdbParser(callback, filters=filters)
    parser.parse(args.rdbfile)
