#!/bin/env python3
import os
import mmap
import logging
import hashlib
import contextlib
log = logging.getLogger(__name__)

@contextlib.contextmanager
def directio_mmap(filename, readsize, offset):
    """Context manager that returns an READ_ONLY O_DIRECT mmap for filename
    Takes a desired readsize, but reduces that to the size of the device to
    prevent errors.
    """
    if offset % mmap.PAGESIZE:
        raise ValueError("Offset must be a multiple of  {}"
                         .format(mmap.PAGESIZE))
    # O_DIRECT means we bypass the file cache
    fd = os.open(filename, os.O_RDONLY | os.O_DIRECT)
    try:
        # ACCESS_READ is necessary since RDONLY is set
        with mmap.mmap(fd, readsize, offset=offset,
                       access=mmap.ACCESS_READ) as mm:
            yield mm
    finally:
        os.close(fd)


def hashfile(filename, size):
    """Hashes a file and returns a hash object"""
    hash = hashlib.sha256()
    offset = 0
    if size == 0:
        size = float('Inf')

    # Find max_size so we don't try to read too much
    with open(filename, 'rb') as f:
        filesize = f.seek(0, 2)
    size = min(size, filesize)

    while offset < size:
        blocksize = min(size - offset, 2**20)
        with directio_mmap(filename, blocksize, offset) as mm:
            offset += len(mm)
            if not mm:
                break
            hash.update(mm)
    log.debug("%s: sha256=%s, %s bytes", filename, hash.hexdigest(), offset)
    return hash
