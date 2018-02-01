from facepy import GraphAPI
import facepy
import re
import json

#meta variables
access_token = 'your_token'
page_id = 'the_page' # input page id here
base_query = page_id + '/feed?limit=300'

# scrape the first page
print 'scraping:', base_query
graph = GraphAPI(access_token)
feed = graph.get(base_query)
data = feed['data']

# determine the next page
next = feed['paging']['next']
next_search = re.search('.*(\&until=[0-9]+)', next, re.IGNORECASE)
if next_search:
    the_until_arg = next_search.group(1)

# scrape the rest of the pages
while (next is not False):
    the_query = base_query + the_until_arg
    print 'baking:', the_query
    try: 
        feed = graph.get(the_query)
        data.append(feed['data'])
    except facepy.exceptions.OAuthError:
        print 'start again at', the_query
        break

    # determine the next page, until there isn't one
    try:
        next = feed['paging']['next']
        next_search = re.search('.*(\&until=[0-9]+)', next, re.IGNORECASE)
        if next_search:
            the_until_arg = next_search.group(1)
    except IndexError:
        print 'last page...'
        next = False  
    total_scraped = total_scraped + 300
    print total_scraped, 'pies in the face so far'
# dump to json
with open('data.json', 'wb') as fp:
    json.dump(data, fp)