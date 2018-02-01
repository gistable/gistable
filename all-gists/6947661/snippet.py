#!/usr/bin/python

# Get the likes of any facebook pages.
#
# You have to install https://github.com/pythonforfacebook/facebook-sdk first.
# Then go to Facebook Graph API Explorer, and copy the Access Token.

import facebook
import sys

token = 'ENTER_YOUR_OAUTH_TOKEN_HERE'


def main(args):
    if len(args) == 1:
        print getLikes(args[0])
    else:
        print 'python get_page_likes.py <page_id>'


def getLikes(id):
    likes = 0

    graph = facebook.GraphAPI(token)
    data = graph.get_object(id)
    if data:
        likes = data['likes']

    return likes


if __name__ == '__main__':
    main(sys.argv[1:])
