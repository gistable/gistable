#!/usr/bin/python3
#
# Simple Bloom filter implementation in Python 3
# Copyright 2017 Hector Martin "marcan" <marcan@marcan.st>
# Licensed under the terms of the MIT license
#
# Written to be used with the Have I been pwned? password list:
#   https://haveibeenpwned.com/passwords
#
# Download the pre-computed filter here (629MB, k=11, false positive p=0.0005):
#   https://mrcn.st/t/pwned-passwords-1.0u2.bloom
# Or if you're more paranoid (924MB, k=16, false positive p=0.000015):
#   https://mrcn.st/t/pwned-passwords-1.0u2-k16.bloom
#
# Also works as a generic file-backed bloom filter for other purposes.
# Use something like this to work out what 'm' and 'k' you need:
#   https://krisives.github.io/bloom-calculator/
# For bulk data loads you should put the bloom filter on a tmpfs/ramdisk,
# as loading directly onto a disk-backed filter is extremely slow.
#
# Examples:
#   $ python bloom.py load -m 5033164800 -k 11 -l passwords.bloom pwned-passwords-1.0.txt
#   $ python bloom.py load -l passwords.bloom pwned-passwords-update-1.txt
#   $ python bloom.py test -s passwords.bloom letmein
#   Found
#   $ python bloom.py test -s passwords.bloom si2v8jX4LG
#   Not found
#
#   $ python3
#   >>> from hashlib import sha1
#   >>> from bloom import BloomFilter
#   >>> filter = bloom.BloomFilter("pwned-passwords-1.0u1.bloom")
#   >>> filter.contains(sha1(b"p4ssword").hexdigest())
#   True
#   >>> filter.contains(sha1(b"super_secure_password").hexdigest())
#   False

import os, json, mmap
from hashlib import md5

class BloomFilter(object):
    ALIGN = 16384
    THRESHOLD = 2**32 # for uniformity, rehash after fewer bits left

    def __init__(self, filename, m=None, k=None, readonly=False):
        self.bits = None

        if os.path.exists(filename):
            self.open(filename, readonly=readonly)
        elif readonly:
            raise IOError("File %s not found" % filename)
        elif m is None or k is None:
            raise ValueError("Filter does not exist and m/k not provided")
        else:
            self.create(filename, m, k)

    def open(self, filename, readonly=True):
        fd = open(filename, "rb" if readonly else "r+b")
        hdr = json.loads(fd.readline().decode("ascii"))
        self.m = hdr["m"]
        self.k = hdr["k"]
        self.size = hdr["size"]
        self.offset = hdr["offset"]
        self.threshold = hdr["threshold"]
        self.bits = mmap.mmap(fd.fileno(), self.size, offset=self.offset, 
                              prot=(mmap.PROT_READ |
                                    (mmap.PROT_WRITE if not readonly else 0)))

    def create(self, filename, m, k):
        fd = open(filename, "w+b")
        size = (m + 7) // 8
        size = (size + self.ALIGN - 1) & ~(self.ALIGN - 1)
        self.m = m
        self.k = k
        self.size = size
        self.offset = self.ALIGN
        self.threshold = self.THRESHOLD
        hdr = {
            "m": m,
            "k": k,
            "offset": self.ALIGN,
            "size": size,
            "threshold": self.THRESHOLD,
        }
        fd.write(json.dumps(hdr).encode("ascii") + b"\n")
        fd.seek(size + self.ALIGN - 1)
        fd.write(b"\x00")
        fd.seek(self.ALIGN)

        self.bits = mmap.mmap(fd.fileno(), self.size, offset=self.offset)

    def hash(self, s):
        capacity = 0
        val = 0
        if isinstance(s, str):
            s = s.encode("utf-8")

        for i in range(self.k):
            if capacity < self.threshold:
                s = md5(s).digest()
                val = int.from_bytes(s, byteorder='big')
                capacity = 1 << 128
            h = val % self.m
            val //= self.m
            capacity //= self.m
            yield h

    def add(self, s):
        for h in self.hash(s):
            byte, bit  = h >> 3, h & 7
            self.bits[byte] |= 1 << bit

    def update(self, iterable):
        for s in iterable:
            for h in self.hash(s):
                byte, bit  = h >> 3, h & 7
                self.bits[byte] |= 1 << bit

    def contains(self, s):
        for h in self.hash(s):
            byte, bit  = h >> 3, h & 7
            if not (self.bits[byte] & (1 << bit)):
                return False
        return True

    def sync(self):
        self.bits.flush()

    def __del__(self):
        if self.bits:
            self.bits.flush()
            self.bits.close()

if __name__ == "__main__":
    import sys, argparse
    from hashlib import sha1

    def cmd_load(args):
        filt = BloomFilter(args.filter, m=args.bits, k=args.hashes)

        if args.sha1:
            if args.lower:
                filt.update(sha1(line.rstrip("\n").lower().encode("utf-8")).hexdigest()
                            for line in open(args.input))
            else:
                filt.update(sha1(line.rstrip("\n").encode("utf-8")).hexdigest()
                            for line in open(args.input))
        else:
            if args.lower:
                filt.update(line.rstrip("\n").lower().encode("utf-8")
                            for line in open(args.input))
            else:
                filt.update(line.rstrip("\n").encode("utf-8")
                            for line in open(args.input))

        filt.sync()

    def cmd_test(args):
        value = args.value.encode("utf-8")
        if args.sha1:
            value = sha1(value).hexdigest()

        filt = BloomFilter(args.filter, readonly=True)
        if filt.contains(value):
            print("Found")
        else:
            print("Not found")

    parser = argparse.ArgumentParser(prog=sys.argv[0], epilog="""
examples:
  %(prog)s load -m 5033164800 -k 11 -l passwords.bloom pwned-passwords-1.0.txt
  %(prog)s load -l passwords.bloom pwned-passwords-update-1.txt
  %(prog)s test -s passwords.bloom letmein
  %(prog)s test -s passwords.bloom si2v8jX4LG""",
    formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="subcommand")
    p_load = subparsers.add_parser('load', help='create or add to a bloom filter')
    p_load.set_defaults(func=cmd_load)
    p_load.add_argument("-m", "--bits", type=int, default=5033164800, help="number of bits in the filter")
    p_load.add_argument("-k", "--hashes", type=int, default=11, help="number of hash functions to use")
    p_load.add_argument("-l", "--lower", action="store_true", help="lowercase input data")
    p_load.add_argument("-s", "--sha1", action="store_true", help="SHA-1 input data")
    p_load.add_argument("filter", type=str, help='filename of the filter')
    p_load.add_argument("input", type=str, help='file containing input data')

    p_test = subparsers.add_parser('test', help='check whether a given value matches the bloom filter')
    p_test.set_defaults(func=cmd_test)
    p_test.add_argument("-s", "--sha1", action="store_true", help="SHA-1 input data")
    p_test.add_argument("filter", type=str, help='filename of the filter')
    p_test.add_argument("value", type=str, help='value to look up in the filter')

    args = parser.parse_args()
    if args.subcommand is None:
        parser.print_help()
        sys.exit(0)

    args.func(args)
