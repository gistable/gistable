#!/usr/bin/env python

from pocket import Pocket
import webbrowser, sys

# Get consumer key from cmd line
consumer_key = sys.argv[1]

request_token = Pocket.get_request_token(
    consumer_key=consumer_key,
    redirect_uri='http://google.com/',
)
auth_url = Pocket.get_auth_url(
    code=request_token,
    redirect_uri='http://google.com/',
)

print '------ '
print 'Now opening a browser tab to authenticate with Pocket'
print 'When finished, press ENTER here...'
print '------ '

# Open web browser tab to authenticate with Pocket
webbrowser.open_new_tab(auth_url)

# Wait for user to hit ENTER before proceeding
raw_input()

access_token = Pocket.get_access_token(
    consumer_key=consumer_key,
    code=request_token,
)
print 'Got authenticated request token - ' + request_token

pocket_instance = Pocket(consumer_key, access_token)

# Retrieve list items
items_list = pocket_instance.get()


def filterurl(url, char):
    ''' Function to prune off extra URL options '''
    try:
        return url[:url.index(char)]
    except ValueError:
        return url

# This dictionary is a straight copy of the data from Pocket, but
# with only the ID and URL properties.
# It will also strip all of the extra social media crap from each URL.
masterdict = {}

for item in items_list[0]['list']:
    article_id = items_list[0]['list'][item]['item_id']
    article_url = items_list[0]['list'][item]['given_url']

    # Remove extra crap from URLS (DANGEROUS - don't remove too much!)
    article_url = filterurl(article_url, '?utm')
    #article_url = filterurl(article_url, '#')

    masterdict[article_id] = article_url

# This dictionary will hold only unique entries
filtereddict = {}

# This loop will find the duplicate URLs and delete them from the list
for k, v in masterdict.iteritems():
    if not v in filtereddict.values():
        filtereddict[k] = v
    else:
        print "Removing duplicate: " + v
        pocket_instance.delete(str(k), wait=False)

print str(len(filtereddict)) + " unique articles in your Pocket list."

print "Done!"
