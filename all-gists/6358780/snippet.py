import pymongo

# Set up DB client, db, collection

date_tweet_count = {}
date_url_count = {}

for user in collection.find():
    for tweet in user['tweets']:
        datestr = tweet['created_at']
        datefields = datestr.split()
        shortdatestr = datefields[-1] + " " + datefields[1] + " " + datefields[2]
        if shortdatestr in date_tweet_count:
            date_tweet_count += 1
            date_url_count += len(tweet['urls'])
        else:
            date_tweet_count = 1
            date_url_count = len(tweet['urls'])
            

datelist = date_tweet_count.keys()  # x-axis
tweetcount = []
for date in datelist:
    tweetcount.append(date_tweet_count[date])

# and the same for urlcountlist