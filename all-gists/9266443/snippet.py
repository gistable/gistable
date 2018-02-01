class MySpider(Spider):
	# [...]
	
	# start requests from generator
	def start_requests(self):
		url = 'http://some.page.tld/%s/category'
		for page in xrange(1, 247):
			link = url % page
			yield Request(url=link)