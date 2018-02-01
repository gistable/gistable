'''
Spider for IMDb
- Retrieve most popular movies & TV series with rating of 8.0 and above
- Crawl next pages recursively
'''

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector

from scrapy_tutorial.items import ScrapyTutorialItem

class IMDbNextPageSpider(CrawlSpider):

	name = "imdbnextpage"
	allowed_domains = ["imdb.com"]
	start_urls = [
		"http://www.imdb.com/search/title?count=20&start=1&title_type=feature,tv_series"
	]
	rules = (
		# Extract links for next pages
		Rule(SgmlLinkExtractor(allow=(), restrict_xpaths=('//div[contains(@class, "leftright")][1]//a[contains(., "Next")]')), callback='parse_listings', follow=True),
	)

	def parse_start_url(self, response):
		'''
		Crawl start_urls
		'''

		return self.parse_listings(response)

	def parse_listings(self, response):
		'''
		Extract data from listing pages
		'''

		sel = Selector(response)
		films = sel.xpath('//table[contains(@class, "results")]//tr[contains(@class, "detailed")]')
		items = []

		for film in films:
			# Populate film fields
			item = ScrapyTutorialItem()
			item['title'] = film.xpath('.//td[contains(@class, "title")]/a/text()').extract()
			item['year'] = film.xpath('.//span[contains(@class, "year_type")]/text()').extract()
			item['rating'] = film.xpath('.//span[contains(@class, "rating-rating")]/span[contains(@class, "value")]/text()').extract()
			item['description'] = film.xpath('.//span[contains(@class, "outline")]/text()').extract()
			item['poster_url'] = film.xpath('.//td[contains(@class, "image")]//img/@src').extract()
			item['film_url'] = film.xpath('.//td[contains(@class, "title")]/a/@href').extract()
			item = self.__normalise_item(item, response.url)

			# Get films with rating of 8.0 and above
			if item['rating'] > 8:
				items.append(item)

		return items

	def __normalise_item(self, item, base_url):
		'''
		Standardise and format item fields
		'''

		# Loop item fields to sanitise data and standardise data types
		for key, value in vars(item).values()[0].iteritems():
			item[key] = self.__normalise(item[key])

		# Clean year and convert year from string to float
		item['year'] = item['year'].strip('()')
		item['type'] = 'Movie'

		if len(item['year']) > 4:
			item['type'] = item['year'][5:]
			item['year'] = item['year'][0:4]
		item['year'] = self.__to_int(item['year'])

		# Convert rating from string to float
		item['rating'] = self.__to_float(item['rating'])

		# Convert film URL from relative to absolute URL
		item['film_url'] = self.__to_absolute_url(base_url, item['film_url'])

		return item

	def __normalise(self, value):
		# Convert list to string
		value = value if type(value) is not list else ' '.join(value)
		# Trim leading and trailing special characters (Whitespaces, newlines, spaces, tabs, carriage returns)
		value = value.strip()

		return value

	def __to_absolute_url(self, base_url, link):
		'''
		Convert relative URL to absolute URL
		'''

		import urlparse

		link = urlparse.urljoin(base_url, link)

		return link

	def __to_int(self, value):
		'''
		Convert value to integer type
		'''

		try:
			value = int(value)
		except ValueError:
			value = 0

		return value

	def __to_float(self, value):
		'''
		Convert value to float type
		'''

		try:
			value = float(value)
		except ValueError:
			value = 0.0

		return value