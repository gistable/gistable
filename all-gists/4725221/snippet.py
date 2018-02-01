import urllib2
import re
import json


def find_review_links(html):
    re.VERBOSE
    # some reviews are listed with the rating in a span tag: <span class="grey">4</span>
    span_re = re.compile(r'''span\sclass=\"?grey\"?\>(\d\.?\d?)''', re.UNICODE | re.IGNORECASE | re.VERBOSE)
    review_ratings = span_re.findall(html)
    # other reviews have the rating in a div: <div class="grey">Rating: 4 / 5</div>
    div_re = re.compile(r'''div\sclass=\"?grey\"?\>Rating:\s(\d\.?\d?)''', re.UNICODE | re.IGNORECASE | re.VERBOSE)
    review_ratings = review_ratings + div_re.findall(html)
    return review_ratings


single_reviews = {}
album_reviews = {}
url = "http://www.residentadvisor.net/reviews.aspx?format=%s&yr=%d&mn=%d"
for year in range(2001, 2013):
    single_reviews[str(year)] = {}
    album_reviews[str(year)] = {}
    for month in range(1, 13):
        # get single reviews
        page = urllib2.urlopen(url % ("single", year, month), timeout=20)
        review_ratings = find_review_links("".join(page.readlines()))
        single_reviews[str(year)][str(month)] = review_ratings
        # get the album reviews
        page = urllib2.urlopen(url % ("album", year, month), timeout=20)
        review_ratings = find_review_links("".join(page.readlines()))
        album_reviews[str(year)][str(month)] = review_ratings


singles = open('/single_review_ratings.json', 'w')
singles.write(json.dumps(single_reviews))
singles.close()

albums = open('/album_review_ratings.json', 'w')
albums.write(json.dumps(album_reviews))
albums.close()
