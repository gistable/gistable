import logging

from math import exp
from random import random
from time import sleep
from time import time
from uuid import uuid1

from redis.exceptions import WatchError

"""
Port of https://github.com/codahale/metrics/blob/development/src/main/java/com/yammer/metrics/stats/ExponentiallyDecayingSample.java
"""

def now():
  """nanosecond timestamp"""
  return int(time()*10**6)

class ExponentiallyDecayingSample(object):
  """
  A forward-decaying reservoir sample, exponentially biased towards the latest entries
  
  @see http://www.research.att.com/people/Cormode_Graham/library/publications/CormodeShkapenyukSrivastavaXu09.pdf
  """
  RESCALE_THRESHOLD = 60*60*10**6  # 1h

  def __init__(self, redis, name, size=1028, alpha=0.015):
    """redis instance, string, int reservoir size, float alpha controls decay factor"""
    self.redis = redis
    self.name = name
    self.size = size
    self.alpha = alpha

    # initialize these values if they don't exist
    t = now()
    redis.pipeline() \
      .setnx(name + '_start_time', t) \
      .setnx(name + '_next_scale_time', t + self.RESCALE_THRESHOLD) \
      .execute()

  def clear(self):
    """reset state to 0"""
    t = now()
    self.redis.pipeline() \
      .delete(self.name) \
      .delete(self.name + '_count') \
      .set(self.name + '_start_time', t) \
      .set(self.name + '_next_scale_time', t + self.RESCALE_THRESHOLD) \
      .execute()

  def size(self):
    """"""
    val = self.redis.zcount(self.name)
    return val is not None and int(val) or 0

  def update(self, val):
    """"""
    return self.update_ts(val, now())

  def update_ts(self, val, tick):
    """Add a value at timestamp tick"""
    priority = self.weight(tick - self.get_start_time()) / max(1e-6, random())
    new_count = self.redis.incr(self.name + '_count')
    val = uuid1().bytes + str(val)  # prefix val with uuid as this is a sorted set, can pull ts from uuid1 later
    if new_count <= self.size:
      self.redis.zadd(self.name, val, priority)  # oh my, this is backwards from the protocol
    else:
      # race cond here where more than one thread sees the same lowest scored value
      # also self.clear() may be called between count and now
      _, first = self.redis.zrange(self.name, 0, 0, withscores=True)[0]
      if first < priority:
        p = self.redis.pipeline()
        p.zremrangebyrank(self.name, 0, 0)  # remove lowest val
        p.zadd(self.name, val, priority)
        p.execute()

    t = now()
    next_time = self.get_next_scale_time()
    if t >= next_time:
      self.rescale(t, next_time)

  def values(self):
    """Retrieve the sample"""
    return [val[16:] for val in self.redis.zrange(self.name, 0, -1)]

  def weight(self, dt):
    """Exponential weighting function"""
    return exp(self.alpha * (float(dt)/10**6))

  def rescale(self, tick, next_time):
    """Private method to adjust all scores relative to a new landmark time"""
    logging.debug('Rescaling!')
    old_time = self.get_start_time()

    # complicated way of doing compare and set on a value
    key = self.name + '_next_scale_time'
    self.redis.watch(key)
    curr_next_time = self.get_next_scale_time()
    if curr_next_time != next_time:
      # somebody else already got to it      
      logging.debug('%s_next_scale_time != current next' % self.name)
      self.redis.unwatch()
      return
    try:
      self.redis.pipeline().set(key, tick + self.RESCALE_THRESHOLD).execute()
    except WatchError, e:
      # somebody else already got to it
      logging.debug('%s_next_scale_time already updated' % self.name)
      return

    tries = 3
    while tries:
      # iterate through the zset and rescale the scores relative to the new landmark
      start_time = now()
      factor = exp(-self.alpha * (float(start_time - old_time)/10**6))  # yay math
      self.redis.watch(self.name)
      vals = self.redis.zrange(self.name, 0, -1, withscores=True)
      p = self.redis.pipeline()
      p.set(self.name + '_start_time', start_time)
      p.delete(self.name)
      for val, score in vals:
        p.zadd(self.name, val, score * factor)
      try:
        p.execute()
        logging.info('Rescale successful! @ factor %s' % factor)
        return
      except WatchError, e:
        sleep(0.01)
        tries -= 1

    # reset next scale time!
    logging.warning('Rescale failed!')

  def get_count(self):
    return int(self.redis.get(self.name + '_count'))

  def get_start_time(self):
    return int(self.redis.get(self.name + '_start_time'))

  def get_next_scale_time(self):
    return int(self.redis.get(self.name + '_next_scale_time'))
