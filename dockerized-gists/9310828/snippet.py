#! /usr/bin/env python3

import requests
import bs4

params = {'auth_token': 'user:token'}

url = 'https://api.pinboard.in/v1/tags/get'

html = requests.get(url, params = params).content
soup = bs4.BeautifulSoup(html)

tags = soup('tag')
tag_tuples = [(tag['tag'], tag['count']) for tag in tags]

tag_tuples_sorted = sorted(tag_tuples, key = lambda x: x[1], reverse = True)

print(['{}: {}'.format(tag, count) for (tag, count) in tag_tuples_sorted])
