# first: pip install requests
# second: python fb_ages.py

import requests
import json
import re
from collections import Counter, OrderedDict

ages = []

# fetch JSON Data
comments = requests.get(
	'http://graph.facebook.com/510085202471863/comments?limit=300').json()

# find valid ages and put them in a list
for comment in comments['data']:
	# find ages with two numbers, ignoring single number ages
	match = re.findall( r'\d{2}', comment['message'])

	# only get ages where the is only one number in comment
	if len(match) == 1:
		ages.append(match[0])

# count & order ages
age_count_dict = OrderedDict(sorted(Counter(ages).items(), key=lambda t: t[1], 
	reverse=True))

# print out age, count and percentage
for age, count in age_count_dict.items():
	print age, count, '%.1f' % round((count / (len(ages)*1.0)) * 100, 2) + '%'