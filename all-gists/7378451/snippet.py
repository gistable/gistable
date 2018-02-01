#!/usr/bin/env python3
"""Emulate bash:

    $ cat /tmp/fifo.tub &
    $ gunzip -c /tmp/filedata.dat.gz > /tmp/fifo.tub

http://stackoverflow.com/questions/19859283/python-subprocess-hangs-with-named-pipes
"""
import os
from contextlib import contextmanager
from shutil     import rmtree
from subprocess import Popen, check_call
from tempfile   import mkdtemp

@contextmanager
def named_pipe():
    dirname = mkdtemp()
    try:
        path = os.path.join(dirname, 'named_pipe')
        os.mkfifo(path)
        yield path
    finally:
        rmtree(dirname)

with named_pipe() as path, Popen(["cat", path]), open(path, 'wb') as f:
    check_call("gunzip -c /tmp/filedata.dat.gz".split(), stdout=f)