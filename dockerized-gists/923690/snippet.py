from json import loads
from urllib2 import HTTPError, urlopen

class Exchange(object):
	def __init__(self, username, key):
		self.username = username
		self.key = key
	
	def getPage(self, url):
		try:
			resp = urlopen(url)
			return resp.read()
		except HTTPError, e:
			return None
	
	def getJson(self, url):
		page = self.getPage(url)
		return None if page == None else loads(page)
	
	def ticker(self):
		return self.getJson('https://btcex.com/ticker.json')
	
	def orderBook(self):
		orders = self.getPage('https://btcex.com/site/orders/2').split('\n')
		return [x.split(',') for x in orders]
	
	def funds(self):
		return self.getJson('https://btcex.com/api/funds?username=%s&token=%s' % (self.username, self.key))
	
	def orders(self):
		return self.getJson('https://btcex.com/api/orders?username=%s&token=%s' % (self.username, self.key))
	
	def sell(self, quantity, price, ttl, all=False):
		return self.getJson('https://btcex.com/api/order?username=%s&token=%s&order_type=%s&quantity_sell=%f&rate=%f&ttl=%s&ask=1' % (
				self.username, self.key, 
				'All-or-None' if all else 'Limit', 
				quantity, price, 
				ttl
			))
	
	def buy(self, quantity, price, ttl, all=False):
		return self.getJson('https://btcex.com/api/order?username=%s&token=%s&order_type=%s&quantity_sell=%f&rate=%f&ttl=%s&ask=0' % (
				self.username, self.key, 
				'All-or-None' if all else 'Limit', 
				quantity, price, 
				ttl
			))
	
	def cancel(self, id):
		return self.getJson('https://btcex.com/api/cancel?username=%s&token=%s&order_id=%s' % (self.username, self.key, id))
