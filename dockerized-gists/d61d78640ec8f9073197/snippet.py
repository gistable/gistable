"""
This script fetches tweets according to the given criteria and saves them in a CSV file. 


How to use it:

- Install the dependencies:
    $ pip install twython unicodecsv

- Go to https://apps.twitter.com and create an application. Under the "Keys and Access Tokens" tab get your keys and insert them below.

- Refer to https://dev.twitter.com/rest/reference/get/search/tweets for parameters and return values. 
"""

from twython import Twython
import unicodecsv


twitter = Twython(
    CONSUMER_KEY,
    CONSUMER_SECRET,
    ACCESS_TOKEN,
    ACCESS_TOKEN_SECRET,
)

TWEET_COUNT = 500
max_id = None

for i in range(0, int(TWEET_COUNT/100)):
    result = twitter.search(
        q='#Hashtag1 OR #Hashtag2 OR @User1 OR @User2',
        result_type='recent',  # popular | mixed | recent
        count=100,
        max_id=max_id,
        # until='2015-11-20',
        # since_id='123456',
        # geocode='37.781157,-122.398720,1mi',
        # lang='tr',
        # include_entities='true',
    )
    f = open('out.csv', max_id and 'ab' or 'wb')
    writer = unicodecsv.writer(f, encoding='utf-8')
    for status in result['statuses']:
        writer.writerow((
            status['user']['screen_name'],
            status['text'],
            status['created_at'],
        ))
    f.close()
    max_id = result['search_metadata']['next_results'].split('max_id=')[1].split('&')[0]
