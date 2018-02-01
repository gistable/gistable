""" stats-for-decause.py

so, 0 years ago is august 2014 to august 2015
1 years ago is august 2013 to august 2014
2 years ago is august 2012 to august 2013, etc..
the anonymous comments don't add up back 2 years ago because the
anonymous format changed in the message payload -- the "contains"
thing doesn't work exactly that far back.

Output:

query is {'topic': 'org.fedoraproject.prod.bodhi.update.comment'}
---------------
0 years ago 19102
1 years ago 16807
2 years ago 11443
3 years ago 0

query is {'topic': 'org.fedoraproject.prod.bodhi.update.comment', 'contains': '"anonymous":false'}
---------------
0 years ago 18732
1 years ago 16345
2 years ago 7140
3 years ago 0

query is {'topic': 'org.fedoraproject.prod.bodhi.update.comment', 'contains': '"anonymous":true'}
---------------
0 years ago 370
1 years ago 462
2 years ago 230
3 years ago 0

query is {'topic': 'org.fedoraproject.prod.copr.build.end'}
---------------
0 years ago 192937
1 years ago 64219
2 years ago 0
3 years ago 0

"""

import copy
import time

import requests

one_minute = 60
one_hour = one_minute * 60
one_day = one_hour * 24
one_month = one_day * 30
one_year = one_day * 365

def get_count(start, finish, query):
    query = copy.copy(query)
    query['start'] = start
    query['end'] = end
    response = requests.get(
        'https://apps.fedoraproject.org/datagrepper/raw',
        params=query,
    )
    data = response.json()
    return data['total']

queries = [
    {
        'topic': 'org.fedoraproject.prod.bodhi.update.comment',
    },
    {
        'topic': 'org.fedoraproject.prod.bodhi.update.comment',
        'contains': '"anonymous":false',
    },
    {
        'topic': 'org.fedoraproject.prod.bodhi.update.comment',
        'contains': '"anonymous":true',
    },
    {
        'topic': 'org.fedoraproject.prod.copr.build.end',
    },
]
for query in queries:
    print "query is", query
    print "---------------"
    for year in range(4):
        end = time.time() - one_year * year
        start = time.time() - one_year * (year + 1)
        print "%i years ago" % year,
        print get_count(start, end, query)
    print