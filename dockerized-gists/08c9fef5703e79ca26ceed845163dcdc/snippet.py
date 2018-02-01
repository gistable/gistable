import time

class Bucket(object):
  def __init__(self, max_amount, refill_time, refill_amount):
    self.max_amount = max_amount
    self.refill_time = refill_time
    self.refill_amount = refill_amount
    self.reset()

  def _refill_count(self):
    return int(((time.time() - self.last_update) / self.refill_time))

  def reset(self):
    self.value = self.max_amount
    self.last_update = time.time()

  def get(self):
    return min(
      self.max_amount,
      self.value + self._refill_count() * self.refill_amount
    )

  def reduce(self, tokens):
    refill_count = self._refill_count()
    self.value += refill_count * self.refill_amount
    self.last_update += refill_count * self.refill_time

    if self.value >= self.max_amount:
      self.reset()
    if tokens > self.value:
      return False

    self.value -= tokens
    return True