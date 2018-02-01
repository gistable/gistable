import urllib, urllib2, json

def search_twitter(query, no_retweets=True):
    if no_retweets:
        # use the negation operator to filter out retweets
        query += ' -RT'

    url = 'http://search.twitter.com/search.json?%s' % urllib.urlencode({
            'q': query,
            'lang': 'en', # restrict results to english tweets
            'rpp': 100, # return 100 results per page (maximum value)
    })
    response = json.loads(urllib2.urlopen(url).read())
    return response['results']