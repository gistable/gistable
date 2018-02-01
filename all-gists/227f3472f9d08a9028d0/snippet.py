import tweepy
from tweepy import OAuthHandler
import io

def twitter_user(username,num):
    fw=io.open("twitter_user.txt",'a',encoding='utf8')
   ckey='Your Consumer Key'
    csecrett='Your Consumer Secret'

    atoken='Your Access Token'
    asecret='Your Access Secret'


    auth=OAuthHandler(ckey,csecret)
    auth.set_access_token(atoken,asecret)

    api=tweepy.API(auth)


    user_tweets=api.user_timeline(screen_name=username,count=num)

    for tweet in user_tweets:
        fw.write(tweet.text+"\n")
        print tweet.text

    fw.close()

user=raw_input("Enter the username: ")
noT=raw_input("Enter the number of tweets required: ")
print "Tweets for the user: "+user+"\n"
twitter_user(user,noT)
