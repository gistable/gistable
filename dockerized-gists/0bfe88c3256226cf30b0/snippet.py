#!/usr/bin/env python
"""\
Extract files from Hotline Miami 2 WAD files.

Usage:
   hlm2-dewad --help
   hlm2-dewad [--flatten] <wad-path> [<path>]
   hlm2-dewad --list <wad-path>

Options:
  --help     Display this help.
  --list     List files.
  --flatten  Don't preserve directories when extracting files.
"""

import collections
import getopt
import os.path
import struct
import sys


# From https://gist.github.com/pollyzoid/bcf01e2adfe1ccd8acbc:
# 
# [Header]
# 4 bytes: File count
# 
# [File metadata]
# <File count> times {
#     4 bytes: Name length
#     <Name length> bytes: Name
#     8 bytes: File size
#     8 bytes: File data offset (starts from end of file metadata section)
# }
# 
# [File data]
# <File count> times {
#     <File size> bytes: File contents
# }


word = struct.Struct('<L')
big_words = struct.Struct('<QQ')

File = collections.namedtuple('File', ['name', 'size', 'offset'])


def read_metadata(fh):
    """
    Given a file handle, this reads the metadata header from it.
    """
    fh.seek(0)
    n_files, = word.unpack(fh.read(word.size))
    for _ in xrange(n_files):
        name_len, = word.unpack(fh.read(word.size))
        name = fh.read(name_len)
        size, offset = big_words.unpack(fh.read(big_words.size))
        yield File(name, size, offset)


def filter_prefix(files, prefix):
    """
    Filter out files not starting with `prefix`.
    """
    # The prefix should always end in a single '/' as it's a directory path.
    prefix = prefix.rstrip('/') + '/'
    for fl in files:
        if fl.name.startswith(prefix):
            yield fl


def flatten_filenames(files):
    """
    Strip out the directory path.
    """
    for fl in files:
        name = os.path.basename(fl.name)
        yield File(name, fl.size, fl.offset)


def list_files(filepath):
    """
    Print out a listing of the files in the WAD.
    """
    with open(filepath, 'rb') as fh:
        for fl in read_metadata(fh):
            try:
                print "%s\t%d" % (fl.name, fl.size)
            except IOError:
                # Cope with broken pipes relatively gracefully.
                break
    return 0


def extract(filepath, prefix, flatten):
    """
    Extract files from the WAD.
    """
    with open(filepath, 'rb') as fh:
        files = read_metadata(fh)
        if prefix is not None:
            files = filter_prefix(files, prefix)
        if flatten:
            files = flatten_filenames(files)
        # This needs to be a list to make sure we've read the whole header.
        files = list(files)
        # After we've read the metadata, we should be at the start of the
        # files.
        offset_base = fh.tell()
        for fl in files:
            fh.seek(offset_base + fl.offset)
            dirname = os.path.dirname(fl.name)
            if dirname != '' and not os.path.exists(dirname):
                os.makedirs(dirname)
            with open(fl.name, 'wb') as ofh:
                ofh.write(fh.read(fl.size))
    return 0


def usage(msg=None):
    if msg is None:
        print __doc__
    else:
        print >> sys.stderr, 'Error:', str(msg)
        print >> sys.stderr
        print >> sys.stderr, __doc__[__doc__.find('\n\nUsage:'):].lstrip()


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], '',
                                   ['help', 'list', 'flatten'])
    except getopt.GetoptError as exc:
        usage(exc)
        return 1

    do_list = False
    flatten = False
    for opt, _ in opts:
        if opt == '--help':
            usage()
            return 0
        elif opt == '--list':
            do_list = True
        elif opt == '--flatten':
            flatten = True

    if len(args) < 1:
        usage('No file path provided.')
        return 1
    filepath = args[0]
    if not os.path.isfile(filepath):
        usage('No such file: %s' % filepath)
        return 2

    prefix = None if len(args) < 2 else args[1]

    if do_list:
        return list_files(filepath)
    return extract(filepath, prefix, flatten)


if __name__ == '__main__':
    sys.exit(main())