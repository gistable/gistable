# This script prints out a list of the TITLES of all posts on a Tumblr blog
#
# TF 2013-01-16


import requests
import sys

if len(sys.argv) != 2:
    print "Usage: " + sys.argv[0] + " blog_name.tumblr.com"
    exit(1);

blog = sys.argv[1]
api_key = 'fuiKNFp9vQFvjLNvx4sUwti4Yb5yGutBN4Xh10LXZhhRKjWlV4' # copied from API example
offset = 0

while 1:
    url = 'http://api.tumblr.com/v2/blog/' + blog + '/posts/text?api_key=' + api_key + '&offset=' + str(offset) + '&notes_info=false'

    r = requests.get(url)
    j = r.json()

    posts = j['response']['posts']

    if len(posts) == 0:
        break

    offset = offset + len(posts)

    for p in posts:
        print p['short_url'] + ' \t' + p['title'] 
