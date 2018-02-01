# Original averaging code from Zed Shaw's Stats class.
# Moving average code by Drew Yeaton.


from math import sqrt
from collections import deque


class SimpleAverage(object):
  def __init__(self, sum=0.0, sumsq=0.0, n=0, minimum=0, maximum=0.0):
    self.sum = sum
    self.sumsq = sumsq
    self.n = n
    self.minimum = minimum
    self.maximum = maximum
  
  
  def __call__(self, s):
    self.sum += s
    self.sumsq += s * s
    if self.n == 0:
      self.minimum = s
      self.maximum = s
    else:
      if self.minimum > s: self.minimum = s
      if self.maximum < s: self.maximum = s
    
    self.n += 1.0
    return self.mean
  
  
  def get_mean(self):
    try:
      return self.sum / self.n
    except ZeroDivisionError:
      return 0.0
  
  
  def get_sd(self):
    try:
      return sqrt((self.sumsq - (self.sum * self.sum / self.n)) / (self.n - 1))
    except ZeroDivisionError:
      return 0.0
  
  
  def __unicode__(self):
    return u'<average Mean:%f, StdDev:%f, Min:%f, Max:%f>' % (self.mean, self.sd, self.minimum, self.maximum)
  
  
  mean = property(get_mean)
  sd = property(get_sd)


class SimpleMovingAverage():
  def __init__(self, period):
    assert period == int(period) and period > 0, 'Period must be an integer greater than 0'
    self.period = period
    self.stream = deque()
    self.mean = None
 
  
  def __call__(self, n):
    stream = self.stream
    stream.append(n)  # appends on the right
    streamlength = len(stream)
    if streamlength > self.period:
      stream.popleft()
      streamlength -= 1
    if streamlength == 0:
      mean = 0
    else:
      mean = sum(stream) / streamlength
    
    self.mean = mean
    return mean
  
  
  def __unicode__(self):
    return '<simpleMovingAverage Mean:%f, StdDev:%f, Min:%f, Max:%f>' % (self.mean, self.sd, self.minimum, self.maximum)
  
  
  maximum = property(lambda self: max(self.stream))
  minimum = property(lambda self: min(self.stream))
  sd = property(lambda self: sqrt((sum([x * x for x in self.stream]) - (sum(self.stream) * sum(self.stream) / self.period)) / (self.period - 1)))


if __name__ == "__main__":
  import random
  
  avg = SimpleAverage()
  for i in range(100):
    i = random.randint(0, 100)
    avg(i)
    print unicode(avg)

  sma = SimpleMovingAverage(10)
  for i in range(100):
    s = float(random.randint(0, 100))
    sma(s)
    print unicode(sma)