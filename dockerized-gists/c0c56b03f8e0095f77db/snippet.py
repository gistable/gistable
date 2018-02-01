from bs4 import BeautifulSoup
from urllib2 import Request, urlopen
import decimal

def findPrice(url, selector):
	userAgent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36"
	req = Request(url, None, {'User-Agent': userAgent})
	html = urlopen(req).read()	
	soup = BeautifulSoup(html, "lxml")
	return decimal.Decimal(soup.select(selector)[0].contents[0].strip().strip("$"))

print findPrice("https://cdn.rawgit.com/brianpursley/661071c026b9bf130971/raw/94a914d15e977150b531c5c44cbee1545f9e70f0/example-scrape-target.html", "#priceRow > div:nth-of-type(2)")

# Below is an example of how you could potentially use this to extract a price from an Amazon product web page
# print findPrice("http://www.amazon.com/Introduction-Algorithms-3rd-Thomas-Cormen/dp/0262033844", "#newOfferAccordionRow .header-price")
