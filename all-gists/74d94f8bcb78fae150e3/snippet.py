#!/usr/bin/env python2

"""Demonstration of a Python logging handler that creates a separate output
file for each stream. The key thing here is the class MultiHandler. It picks
the file name based on the thread name; could use anything in threading.local()
"""

import threading, logging, time, random, os

# Global object we log to; the handler will work with any log message
_L = logging.getLogger("demo")

# Create a special logger that logs to per-thread-name files
# I'm not confident the locking strategy here is correct, I think this is
# a global lock and it'd be OK to just have a per-thread or per-file lock.
class MultiHandler(logging.Handler):
    def __init__(self, dirname):
        super(MultiHandler, self).__init__()
        self.files = {}
        self.dirname = dirname
        if not os.access(dirname, os.W_OK):
            raise Exception("Directory %s not writeable" % dirname)

    def flush(self):
        self.acquire()
        try:
            for fp in self.files.values():
                fp.flush()
        finally:
            self.release()

    def _get_or_open(self, key):
        "Get the file pointer for the given key, or else open the file"
        self.acquire()
        try:
            if self.files.has_key(key):
                return self.files[key]
            else:
                fp = open(os.path.join(self.dirname, "%s.log" % key), "a")
                self.files[key] = fp
                return fp
        finally:
            self.release()

    def emit(self, record):
        # No lock here; following code for StreamHandler and FileHandler
        try:
            fp = self._get_or_open(record.threadName)
            msg = self.format(record)
            fp.write('%s\n' % msg.encode("utf-8"))
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

# A simple task that spams log messages at random intervals
class Task(object):
    def __init__(self, r=3):
        self.run_for = r

    def run(self):
        start_time = time.time()
        end_time = time.time() + self.run_for
        while time.time() < end_time:
            nap_time = min(random.uniform(0.3, 1.5), end_time - time.time())
            time.sleep(nap_time)
            _L.info(u"Been running %.2fs \u2603" % (time.time() - start_time))


### Set up basic stderr logging; this is nothing fancy.
log_format = '%(relativeCreated)6.1f %(threadName)12s: %(levelname).1s %(module)8.8s:%(lineno)-4d %(message)s'
stderr_handler = logging.StreamHandler()
stderr_handler.setFormatter(logging.Formatter(log_format))
logging.getLogger().addHandler(stderr_handler)

### Set up a logger that creates one file per thread
multi_handler = MultiHandler("/tmp")
multi_handler.setFormatter(logging.Formatter(log_format))
logging.getLogger().addHandler(multi_handler)

### Set default log level, log a message
_L.setLevel(logging.DEBUG)
_L.info("Run initiated")

### Create some tasks and run them with Thread names
tasks = (("red", Task()),
         ("green", Task()),
         ("blue", Task()))
for name, task in tasks:
    thread = threading.Thread(target=task.run, name=name)
    thread.start()

