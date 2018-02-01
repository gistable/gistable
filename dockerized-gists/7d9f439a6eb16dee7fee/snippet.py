import tweepy
import pymongo

# Tweepy API doc here: http://pythonhosted.org/tweepy/html/api.html
# PyMongo API doc here: https://pypi.python.org/pypi/pymongo/

# Keys
consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''

# Twitter initialization
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# Mongo initialization
client = pymongo.MongoClient("localhost", 27017)
db = client.financials

try:
    statuses = api.list_timeline(api.me().screen_name, '<NAME OF TIMELINE?>')
    for s in statuses:
        if db.news.find_one({'text':s.text}) == None: # prevent duplicate tweets being stored
            news = {'text':s.text, 'id':s.id, 'created_at':s.created_at,'screen_name':s.author.screen_name,'author_id':s.author.id}
            db.news.save(news)
except tweepy.error.TweepError:
    print "Whoops, could not fetch news!"
except UnicodeEncodeError:
    pass
