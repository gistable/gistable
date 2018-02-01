# Copyright 2016, Takuya Akiba
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#     * Neither the name of Takuya Akiba nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import logging
import sys
import collections
import os
import time
import datetime
import json


dict_type = collections.OrderedDict
jlog = dict_type()
_stack = [jlog]


def get(key=None):
    if not key:
        return _stack[-1]

    if type(key) == str:
        key = key.split('.')
    assert type(key) == list

    j = _stack[-1]
    for k in key:
        assert type(j) == dict_type
        if k not in j:
            j[k] = dict_type()
        j = j[k]
    return j


def put(key, value):
    logging.info("{0}{1} = {2}".format(' ' * (len(_stack) - 1), key, value))
    ks = key.split('.')
    j = get(ks[0:-1])
    j[ks[-1]] = value


def add(key, value):
    logging.info("{0}{1} = {2}".format(' ' * len(_stack), key, value))
    ks = key.split('.')
    j = get(ks[0:-1])
    k = ks[-1]
    if k not in j:
        j[k] = list()
    j[k].append(value)


class open:
    def __init__(self, key):
        logging.info("{0}{1}:".format(' ' * (len(_stack) - 1), key))
        self.j = get(key)

    def __enter__(self):
        _stack.append(self.j)

    def __exit__(self, exc_type, exc_val, exc_tb):
        assert _stack[-1] == self.j
        _stack.pop()


class add_open:
    def __init__(self, key):
        logging.info("{0}{1}:".format(' ' * (len(_stack) - 1), key))
        key = key.split('.')
        j = get(key[0:-1])
        k = key[-1]
        if k not in j:
            j[k] = list()
        assert type(j[k]) == list
        j[k].append(dict_type())
        self.j = j[k][-1]

    def __enter__(self):
        _stack.append(self.j)

    def __exit__(self, exc_type, exc_val, exc_tb):
        assert _stack[-1] == self.j
        _stack.pop()


class put_benchmark:
    def __init__(self, key):
        self.key = key

    def __enter__(self):
        self.t = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        put(self.key, time.time() - self.t)


class add_benchmark:
    def __init__(self, key):
        self.key = key

    def __enter__(self):
        self.t = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        add(self.key, time.time() - self.t)


def setup():
    with open('run'):
        put('program', sys.argv[0])
        put('argv', sys.argv)
        put('hostname', os.uname().nodename)
        put('pid', os.getpid())
        put('start_datetime', '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))


def finalize():
    with open('run'):
        now = datetime.datetime.now()
        put('end_datetime', '{:%Y-%m-%d %H:%M:%S}'.format(now))
        s = datetime.datetime.strptime(get('start_datetime'), '%Y-%m-%d %H:%M:%S')
        put('wall_time', (now - s).total_seconds())


def example():
    logging.basicConfig(level=logging.INFO)

    setup()

    put("hoge", 10)
    put("cat.nya.meow", 123)

    with open("piyo.very.useful.open"):
        put("fuga", [1, 2, 3])
        put("pya-", ['hey', 'yo'])

    for i in range(3):
        with add_open('piyo.add_open'):
            put('a', i)
            put('b', i * i)

    add("risuto.dayo", 1)
    add("risuto.dayo", 10)
    add("risuto.dayo", 100)

    import pprint
    pprint.pprint(jlog)


if __name__ == "__main__":
    example()
