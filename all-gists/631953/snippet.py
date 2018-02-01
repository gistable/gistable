"""
A decorator for management commands (or any class method) to ensure that there is
only ever one process running the method at any one time.

Requires lockfile - (pip install lockfile)

Author: Ross Lawley
"""

import time
import logging

from lockfile import FileLock, AlreadyLocked, LockTimeout
from django.conf import settings

# Lock timeout value - how long to wait for the lock to become available.
# Default behavior is to never wait for the lock to be available (fail fast)
LOCK_WAIT_TIMEOUT = getattr(settings, "DEFAULT_LOCK_WAIT_TIMEOUT", -1)

def handle_lock(handle):
    """
    Decorate the handle method with a file lock to ensure there is only ever
    one process running at any one time.
    """
    
    def wrapper(self, *args, **options):
        
        start_time = time.time()
        verbosity = options.get('verbosity', 0)
        if verbosity == 0:
            level = logging.WARNING
        elif verbosity == 1:
            level = logging.INFO
        else:
            level = logging.DEBUG
        
        logging.basicConfig(level=level, format="%(message)s")
        logging.debug("-" * 72)
        
        lock_name = self.__module__.split('.').pop()
        lock = FileLock(lock_name)
        
        logging.debug("%s - acquiring lock..." % lock_name)
        try:
            lock.acquire(LOCK_WAIT_TIMEOUT)
        except AlreadyLocked:
            logging.debug("lock already in place. quitting.")
            return
        except LockTimeout:
            logging.debug("waiting for the lock timed out. quitting.")
            return
        logging.debug("acquired.")
        
        try:
            handle(self, *args, **options)
        except:
            import traceback
            logging.warn("Command Failed")
            logging.warn('==' * 72)
            logging.warn(traceback.format_exc())
            logging.warn('==' * 72)
        
        logging.debug("releasing lock...")
        lock.release()
        logging.debug("released.")
        
        logging.info("done in %.2f seconds" % (time.time() - start_time))
        return
        
    return wrapper
