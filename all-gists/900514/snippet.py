from twitter_search import search_twitter
import random
import sys
import re

class Thingy(object):
	def __init__(self, words):
		self.words = words
		self.begins = dict([(word, []) for word in words])
		self.ends = dict([(word, []) for word in words])
	def start(self):
		import urllib
		query = '?' + urllib.urlencode({'q': ' OR '.join(self.words), 'rpp': 100})
		search_twitter(query, self.feed, maxpages=20)
	def feed(self, tweet):
		text = tweet['text']
		for s in self.words:
			loc = text.find(s.lower())
			if loc != -1:
				begins = text[loc:].split(" ")[:random.randrange(2,8)]
				ends = text[:loc+len(s)].split(" ")[-random.randrange(2,8):]
				self.begins[s].append(begins)
				self.ends[s].append(ends)
		
	def generate(self):
		for i in range(1000):
			s = random.choice(self.words)
			begin = ' '.join(random.choice(self.begins[s]))
			end = ' '.join(random.choice(self.ends[s]))
			begin2 = ' '.join(random.choice(self.begins[s]))
			begin3 = ' '.join(random.choice(self.begins[s]))
			target = '\n\t'.join([': '.join([end, begin]), begin2, begin3])
			if re.search(r'^[a-zA-Z,.:;?!\- \n\t]*$', target):
				print target

generator = Thingy(['voicing', 'shucked', 'slant'])
generator.start()
generator.generate()
