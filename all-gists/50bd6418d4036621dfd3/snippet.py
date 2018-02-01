# Get details about own user
me = api.me()
friends = api.friends_ids(me.id)

# Initialize data structure
tweets = {}

# Fetch lists recent tweets for each of the user IDs in the list 'friends'
for user in friends:
    # Only query Twitter for data not already cached
    if db.tweets.find({'user_id': user}).count() == 0:
        print('Get recent tweets for user {}...'.format(user))
        tweets[user] = []
        
        # Query Twitter API for 2 pages (= 40 tweets)
        for page in tweepy.Cursor(api.user_timeline, id=user).pages(2):
            tweets[user].extend(page)
            print('  Got {} tweets so far...'.format(len(tweets[user])))
            # API is rate limited (5 sec sleep = 180 reqs in 15 min)
            time.sleep(5)
            
        # Save each tweet to database
        for tweet in tweets[user]:
            db.tweets.insert_one({'user_id': user, 'tweet': tweet._json})