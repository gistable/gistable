#!/usr/bin/env python3

import os
import sys
import textwrap
import time

def usage():
    print(textwrap.dedent("""
    Usage: {} <pipepath>
    Create a named pipe, send its contents to stdout forever.

    Supplied pipe path must not exist.
    Warning: supplied pipe path will be deleted after a keyboard interrupt.
    """.format(sys.argv[0])).strip())

def read_loop(f):
    while True:
        data = f.read()
        if data:
            sys.stdout.write(data)
            sys.stdout.flush()
        else:
            time.sleep(0.1)

def make_pipe(pipe_fname):
    try:
        os.mkfifo(pipe_fname)
    except OSError as e:
        print("Failed to create named pipe {}".format(pipe_fname))
        print("Error:", e)
        sys.exit(1)

def main(pipe_fname):
    make_pipe(pipe_fname)
    try:
        with open(pipe_fname) as fifo:
            read_loop(fifo)
    except KeyboardInterrupt:
        print()
    finally:
        os.unlink(pipe_fname)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        usage()