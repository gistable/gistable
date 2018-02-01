#!/usr/bin/python

class TokenBucket:
	from time import sleep, time

	def __init__(self, rate, burst = None):
		'Rate in tokens per second, burst in number of tokens'

		self.rate = float(rate)
		if burst is None:
			burst = self.rate
		self.rate = 1 / self.rate
		self.burst = float(burst) * self.rate
		self.toks = self.burst
		self.last = self.now()
	
	def now(self):
		return self.time()

	def rate_limit(self, tokens = 1.0):
		tokens = float(tokens)

		if self.rate <= 0:
			return

		h = self.now()
		diff = h - self.last
		self.toks += diff
		self.last = h

		if self.toks > self.burst:
			self.toks = self.burst

		if self.toks >= self.rate:
			self.toks -= self.rate

		if self.toks < self.rate:
			print 'sleep for %f'%(self.rate - self.toks)
			self.sleep((self.rate - self.toks))

if __name__ == '__main__':
	tbf = TokenBucket(2.0, 5.0)
	while True:
		tbf.rate_limit()
		print '.'
	raise SystemExit, 0