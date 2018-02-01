'''
Spider for IMDb
- Retrieve most popular movies & TV series with rating of 8.0 and above that have at least 5 award nominations
- Crawl next pages recursively
- Follow the details pages of scraped films to retrieve more information of each film
'''

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from scrapy.http.request import Request

from scrapy_tutorial.items import ScrapyTutorialItem

class IMDbDetailsPageSpider(CrawlSpider):

	name = "imdbdetailspage"
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
		Crawl start URLs
		'''

		return self.parse_listings(response)

	def parse_listings(self, response):
		'''
		Extract data from listing pages
		'''

		sel = Selector(response)
		films = sel.xpath('//table[contains(@class, "results")]//tr[contains(@class, "detailed")]')

		for film in films:
			rating = film.xpath('.//span[contains(@class, "rating-rating")]/span[contains(@class, "value")]/text()').extract()
			rating = self.__normalise(rating)
			rating = self.__to_float(rating)

			# Get films with rating of 8.0 and above
			if rating > 8:
				film_url = film.xpath('.//td[contains(@class, "title")]/a/@href').extract()
				film_url = self.__normalise(film_url)
				film_url = self.__to_absolute_url(response.url, film_url)

				yield Request(film_url, callback=self.parse_details)

	def parse_details(self, response):
		'''
		Extract data from details pages
		'''

		sel = Selector(response)
		film = sel.xpath('//div[@id="content-2-wide"]')

		# Populate film fields
		item = ScrapyTutorialItem()
		item['title'] = film.xpath('.//h1/span[contains(@class, "itemprop")]/text()').extract()
		item['year'] = film.xpath('.//div[@id="ratingWidget"]/p[1]/strong/following-sibling::node()').extract()
		item['rating'] = film.xpath('.//span[@itemprop="ratingValue"]/text()').extract()
		item['num_of_nominations'] = film.xpath('.//*[@itemprop="awards"][contains(., "nominations")]/text()').extract()
		item['description'] = film.xpath('.//p[@itemprop="description"]/text()').extract()
		item['poster_url'] = film.xpath('.//*[@id="img_primary"]//img/@src').extract()
		item['film_url'] = response.url
		item = self.__normalise_item(item, response.url)

		# Get films with at least 5 award nominations
		if item['num_of_nominations'] >= 5:
			return item

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
			item['type'] = 'TV Series'
			item['year'] = item['year'][0:4]
		item['year'] = self.__to_int(item['year'])

		# Convert rating from string to float
		item['rating'] = self.__to_float(item['rating'])

		# Convert no. of nominations from string to int
		if item['num_of_nominations']:
			item['num_of_nominations'] = item['num_of_nominations'].split('&')[1]
			item['num_of_nominations'] = [int(s) for s in item['num_of_nominations'].split() if s.isdigit()][0]
		else:
			item['num_of_nominations'] = 0

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