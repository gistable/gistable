#!/usr/bin/env python
from __future__ import print_function
import sys
import os
import re
import ctypes
import argparse

ulseek = ctypes.cdll['libc.so.6'].lseek
ulseek.restype = ctypes.c_uint64
ulseek.argtypes = [ctypes.c_int, ctypes.c_uint64, ctypes.c_int]

def seek_set(fd, pos):
    # lseek casting to 64-bit unsigned
    ctypes.set_errno(0)
    ret = ulseek(fd, pos, os.SEEK_SET)
    if ctypes.get_errno() != 0:
        raise OSError(ctypes.get_errno())

def dump(pid, out):
    # Adapted from http://unix.stackexchange.com/a/6302/39407
    maps_file = open("/proc/%d/maps" % pid, 'r')
    mem_file = os.open("/proc/%d/mem" % pid, os.O_RDONLY)

    for line in maps_file.readlines():  # for each mapped region
        m = re.match(r'([0-9A-Fa-f]+)-([0-9A-Fa-f]+) ([-r])', line)
        if m.group(3) == 'r': # if this is a readable region
            start = int(m.group(1), 16)
            end = int(m.group(2), 16)

            # seek to region start
            seek_set(mem_file, start)
            # read region contents
            chunk = os.read(mem_file, end - start)
            # dump contents to standard output
            out.write(chunk)

    maps_file.close()
    os.close(mem_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dumps a process' memory")
    parser.add_argument('pid', type=int)
    args = parser.parse_args()

    if sys.stdout.isatty():
        print("Refusing to dump memory to a tty. Use a pipe.", file=sys.stderr)
        sys.exit(1)

    if sys.version_info >= (3, ):
        stdout = sys.stdout.buffer
    else:
        stdout = sys.stdout

    dump(args.pid, stdout)