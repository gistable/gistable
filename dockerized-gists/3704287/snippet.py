from __future__ import with_statement
import os
import time
import fcntl
import contextlib

@contextlib.contextmanager
def file_lock(filename, lock_type, timeout=None):
    fd = open(filename, 'w')
    fctnl_lock_type = getattr(fcntl, lock_type, None)
    if fctnl_lock_type is None:
        raise RuntimeError('Cannot find lock_type %s' % lock_type)
    # try to acquire the lock
    if timeout is not None:
        for i in xrange(int(timeout * 10)):
            try:
                fcntl.flock(fd, fctnl_lock_type | fcntl.LOCK_NB)
                break
            except IOError:
                pass
            time.sleep(0.1)
        else:
            fd.close()
            raise IOError('Unable to acquire lock for %s' % filename)
    else:
        fcntl.flock(fd, fctnl_lock_type)

    # execute the main function
    try:
        # ... right here
        yield
    finally:
        # release the lock by closing the file
        fd.close()