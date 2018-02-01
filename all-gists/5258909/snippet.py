import errno
import signal

import zmq


def uninterruptible(f, *args, **kwargs):
    while True:
      try:
        return f(*args, **kwargs)
      except zmq.ZMQError as e:
        if e.errno == errno.EINTR:
          # interrupted, try again
          continue
        else:
          # real error, raise it
          raise

ctx = zmq.Context()
s = ctx.socket(zmq.PULL)
poller = zmq.Poller()
poller.register(s, zmq.POLLIN)

def got_sigint(*a, **kw):
    print("\nSIGINT")

signal.signal(signal.SIGINT, got_sigint)

print("polling, try ^C")

try:
    poller.poll()
except Exception as e:
    print("oops, raised %s" % e)

print("polling again, should be uninterruptible this time")

try:
    uninterruptible(poller.poll, 2000)
except Exception as e:
    print("oops, raised %s" % e)
else:
    print("yup!")
