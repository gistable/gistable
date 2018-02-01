import threading
import time

class TRLock(threading._RLock):
    """Implemention of RLock with a timeout
    Works around http://bugs.python.org/issue13697
    """
    def __init__(self, default_timeout_s=None, *args, **kwargs):
        super(TRLock, self).__init__(*args, **kwargs)
        self.default_timeout_s = default_timeout_s

    def __enter__(self):
        if self.default_timeout_s is not None:
            def closed_acquire():
                gotit = self.acquire_with_timeout(self.default_timeout_s)
                if not gotit:
                    raise RuntimeError('Could not get lock')
            return closed_acquire
        return super(TRLock).__enter__

    def __exit__(self, t, v, tb):
        try:
            self.release()
        except Exception:
            # If we ended up in a timeout situation we might not be the owner
            pass
          
    def acquire_with_timeout(self, timeout_s):
        """Taken from threading._Condition.wait
        Returns True if lock acquired
        Returns False if lock was not acquired$
        """
        # Balancing act:  We can't afford a pure busy loop, so we
        # have to sleep; but if we sleep the whole timeout time,
        # we'll be unresponsive.  The scheme here sleeps very
        # little at first, longer as time goes on, but never longer
        # than 20 times per second (or the timeout time remaining).
        endtime = time.time() + timeout_s
        delay = 0.0005 # 500 us -> initial delay of 1 msQ
        gotit = False
        while True:
            gotit = self.acquire(blocking=False)
            if gotit:
                break
            remaining = endtime - time.time()
            if remaining <= 0:
                break
            delay = min(delay * 2, remaining, .05)
            time.sleep(delay)
        if gotit:
            return True
        return False