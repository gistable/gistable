#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import sys


class InvalidJSONError(ValueError):
    def __init__(self, key, *args, **kwargs):
        self.key = key
        super(InvalidJSONError, self).__init__(key, *args, **kwargs)


def makepair(pair):
    """Return a (key, value) tuple from a KEY=VALUE formatted string.

    Most of the time, both the key and value are strings.
    >>> makepair("foo=bar")
    ('foo', 'bar')

    But integers and floats are recognized too.
    >>> makepair("foo=42")
    ('foo', 42)
    >>> makepair("foo=4.20")
    ('foo', 4.2)

    You can force values to be strings by surrounding them with double quotes.
    >>> makepair('foo="69"')
    ('foo', '69')

    Pairs without an = delimiter have the value None.
    >>> makepair("foo")
    ('foo', None)

    If you need to insert raw JSON values, you can do it with KEY:=VALUE format.
    >>> makepair("foo:=[1, 2, 3]")
    ('foo', [1, 2, 3])
    """

    parts = pair.split('=', 1)
    if len(parts) == 1:
        parts.append(None)
    key, value = parts
    if key[-1] == ":":
        key = key[:-1]
        try:
            value = json.loads(value)
        except ValueError:
            raise InvalidJSONError(key)
    elif value is not None:
        try:
            value = int(value)
        except ValueError:
            try:
                value = float(value)
            except ValueError:
                if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
                    value = value[1:-1]
    return key, value


def fatal(msg, code=1):
    sys.stderr.write("{}: {}\n".format(os.path.basename(sys.argv[0]), msg))
    sys.exit(code)


def main():
    try:
        result = dict(makepair(pair) for pair in sys.argv[1:])
        sys.stdout.write(json.dumps(result))
    except InvalidJSONError as e:
        fatal("valid JSON value required for key `{}'".format(e.key))

if __name__ == '__main__':
    main()
