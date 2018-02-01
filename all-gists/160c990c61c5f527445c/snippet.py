#!/bin/env python3
from pocket import Pocket
consumer_key = "123-2343-4234-32-4-3-4"
'''
redirect_uri = "http://example.com/"
request_token = Pocket.get_request_token(consumer_key=consumer_key, redirect_uri=redirect_uri)

# URL to redirect user to, to authorize your app
auth_url = Pocket.get_auth_url(code=request_token, redirect_uri=redirect_uri)
input(auth_url)

user_credentials = Pocket.get_credentials(consumer_key=consumer_key, code=request_token)

access_token = user_credentials['access_token']

print(access_token);
'''
access_token="23432-4324321432-4-2134-324"
pocket = Pocket(consumer_key, access_token)

lasturl = "http://www.economist.com/news/asia/21678115-display-amity-points-tougher-times-ahead-leaders-taiwan-and-china-hold-historic";
while True:
    stack = [];
    import itertools
    for i in itertools.count(0):
        from urllib.request import urlopen, Request
        from bs4 import BeautifulSoup
        request = Request("http://www.economist.com/latest-updates?page=" + str(i), headers={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0}"})
        bs = BeautifulSoup(urlopen(request))

        for article in bs.find_all("article"):
            from urllib.parse import urljoin
            url = urljoin(request.full_url, article.a['href'])
            if url == lasturl:
                break;
            stack.append(url)
        if url == lasturl:
            break;
    for url in reversed(stack):
        print(url)
        pocket.add(url, wait=False)
    if len(stack) > 0:
        lasturl = stack[-1]
    from time import sleep
    sleep(300)

