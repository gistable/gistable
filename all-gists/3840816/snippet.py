from abc import ABCMeta, abstractmethod
import threading


class ClockInterface(object):
  __metaclass__ = ABCMeta

  @abstractmethod
  def time(self):
    pass

  @abstractmethod
  def tick(self, amount):
    pass

  @abstractmethod
  def sleep(self, amount):
    pass


class Handshake(object):
  def __init__(self):
    self._syn_event = threading.Event()
    self._ack_event = threading.Event()

  def syn(self):
    self._syn_event.wait()
    self._ack_event.set()

  def ack(self):
    self._syn_event.set()
    self._ack_event.wait()


class ThreadedClock(ClockInterface):
  def __init__(self):
    self._time = 0
    self._waiters = []  # queue of [stop time, Handshake]

  def time(self):
    return self._time

  def _pop_waiter(self, end):
    times_up = sorted((waiter for waiter in self._waiters if waiter[0] <= end),
                       key=lambda element: element[0])
    if times_up:
      waiter = times_up[0]
      self._waiters.remove(waiter)
      return waiter

  def tick(self, amount):
    now = self._time
    end = now + amount

    while True:
      waiter = self._pop_waiter(end)
      if not waiter:
        break

      waiter_time, waiter_handshake = waiter
      self._time = waiter_time
      waiter_handshake.ack()

    self._time = end

  def sleep(self, amount):
    waiter_end = self._time + amount
    waiter_handshake = Handshake()

    self._waiters.append((waiter_end, waiter_handshake))
    waiter_handshake.syn()
