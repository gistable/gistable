#!/usr/bin/env python
import urllib
import pprint
import amazonproduct
from BeautifulSoup import BeautifulSoup
from review import db

AWS_KEY = 'YOUR_AWS_KEY'
SECRET_KEY = 'YOUR_AWS_SECRET_KEY'
API_PAGE_LIMIT = 10

REVIEW_URL = r"http://www.amazon.com/product-reviews/%s/"
REVIEW_URL += r"ref=cm_cr_pr_top_link_1?ie=UTF8&pageNumber=%s&showViewpoints=0&sortBy=bySubmissionDateDescending"


# search for a keyword and get ASINs for returned results
# returns list of ASINs
def get_asin(product_type, keyword, associate_tag, callback=None):
    api = amazonproduct.API(AWS_KEY, SECRET_KEY, 'us', associate_tag=associate_tag)
    asin_list = []
    results = api.item_search(product_type, Title=keyword, IncludeReviewsSummary=True)
    for page in results:
        asin_list.extend([unicode(b.ASIN) for b in page.Items.Item])
        if results.current >= API_PAGE_LIMIT:
            break

    return asin_list

# Parse a url for product reviews
# return tuple of (review text, rating)
def parse_reviews(url):
    # sample url for prod review
    #http://www.amazon.com/product-reviews/B0006GBDZY/pageNumber=2
    data = urllib.urlopen(url).read()
    soup = BeautifulSoup(data)
    reviews = []
    for rawreview in soup.findAll('span','swSprite'):
        text = rawreview.parent.parent.parent.text
        if text.startswith("Report abuse"):
            continue
        if text.rfind('YesNoReport abuse|Permalink') < 0:
            continue

        ratingindex = text.index('review helpful') + 14
        startindex = text.index('5 stars') + 7
        endindex = text.index('Help other customers find the most helpful review')
        if ratingindex > startindex:
            ratingindex = 0

        ratingtext = text[ratingindex:startindex]
        #print ratingtext
        rating = float(ratingtext.split()[0])
        text = text[startindex:endindex]
        reviews.append((text, rating))
    return reviews

# Do something with the data here
def store_reviews(product_id, reviews, src="amzn"):
    added_count = 0
    for (data,rating) in reviews:
        print "downloaded review len(%s)/rating(%s)" % (len(data), rating)
        # TODO: process data here
        #
        added_count += 1
    return added_count


# Download all reviews for a giving product id (ASIN)
def download_reviews(product_id):
    print "download product", product_id
    while True:
        url = REVIEW_URL % (product_id, i)
        print "URL", url
        reviews = parse_reviews(url)
        added = store_reviews(product_id, reviews)
        if added == 0:
            break


def main():
    asins = get_asin("Books", "machine learning", None)
    for asin in asins:
        download_reviews(asin)


if __name__=="__main__":
    main()
