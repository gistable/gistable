import tweepy
from tweepy import Cursor
import unicodecsv
from unidecode import unidecode

# Authentication and connection to Twitter API.
consumer_key = ""
consumer_secret = ""
access_key = ""
access_secret = ""

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

# Usernames whose tweets we want to gather.
users = ["lisamurkowski",
"SenJohnMcCain",
"JeffFlake",
"SenMarkPryor",
"JohnBoozman",
"SenFeinstein",
"SenatorBoxer",
"MarkUdall",
"SenBennetCO",
"ChrisMurphyCT",
"SenBlumenthal",
"SenatorCarper",
"ChrisCoons",
"marcorubio",
"SaxbyChambliss",
"brianschatz",
"maziehirono",
"MikeCrapo",
"SenatorRisch",
"SenatorDurbin",
"SenDonnelly",
"SenDanCoats",
"ChuckGrassley",
"SenatorHarkin",
"SenPatRoberts",
"JerryMoran",
"SenRandPaul",
"SenLandrieu",
"DavidVitter",
"SenatorBarb",
"MarkeyMemo",
"stabenow",
"amyklobuchar",
"SenatorWicker",
"clairecmc",
"RoyBlunt",
"jontester",
"SenatorFischer",
"SenatorReid",
"SenDeanHeller",
"SenatorShaheen",
"kellyayotte",
"CoryBooker",
"SenatorMenendez",
"MartinHeinrich",
"SenatorTomUdall",
"SenSchumer",
"SenGillibrand",
"SenatorBurr",
"SenatorHagan",
"SenatorHeitkamp",
"SenJohnHoeven",
"SenSherrodBrown",
"robportman",
"jiminhofe",
"RonWyden",
"SenToomey",
"SenJackReed",
"SenWhitehouse",
"GrahamBlog",
"SenatorTimScott",
"SenJohnThune",
"SenTedCruz",
"SenMikeLee",
"SenatorLeahy",
"timkaine",
"SenRockefeller",
"Sen_JoeManchin",
"SenRonJohnson",
"SenatorEnzi",
"SenJohnBarrasso"]

with open('tweets.csv', 'wb') as file:
    writer = unicodecsv.writer(file, delimiter = ',', quotechar = '"')
    # Write header row.
    writer.writerow(["politician_name",
                    "politician_username",
                    "politician_followers_count",
                    "politician_listed_count",
                    "politician_following",
                    "politician_favorites",
                    "politician_verified",
                    "politician_default_profile",
                    "politician_location",
                    "politician_time_zone",
                    "politician_statuses_count",
                    "politician_description",
                    "politician_geo_enabled",
                    "politician_contributors_enabled",
                    "tweet_year",
                    "tweet_month",
                    "tweet_day",
                    "tweet_hour",
                    "tweet_text",
                    "tweet_lat",
                    "tweet_long",
                    "tweet_source",
                    "tweet_in_reply_to_screen_name",
                    "tweet_direct_reply",
                    "tweet_retweet_status",
                    "tweet_retweet_count",
                    "tweet_favorite_count",
                    "tweet_hashtags",
                    "tweet_hashtags_count",
                    "tweet_urls",
                    "tweet_urls_count",
                    "tweet_user_mentions",
                    "tweet_user_mentions_count",
                    "tweet_media_type",
                    "tweet_contributors"])

    for user in users:
        user_obj = api.get_user(user)

        # Gather info specific to the current user.
        user_info = [user_obj.name,
                     user_obj.screen_name,
                     user_obj.followers_count,
                     user_obj.listed_count,
                     user_obj.friends_count,
                     user_obj.favourites_count,
                     user_obj.verified,
                     user_obj.default_profile,
                     user_obj.location,
                     user_obj.time_zone,
                     user_obj.statuses_count,
                     user_obj.description,
                     user_obj.geo_enabled,
                     user_obj.contributors_enabled]

        # Get 1000 most recent tweets for the current user.
        for tweet in Cursor(api.user_timeline, screen_name = user).items(1000):
            # Latitude and longitude stored as array of floats within a dictionary.
            lat = tweet.coordinates['coordinates'][1] if tweet.coordinates != None else None
            long = tweet.coordinates['coordinates'][0] if tweet.coordinates != None else None
            # If tweet is not in reply to a screen name, it is not a direct reply.
            direct_reply = True if tweet.in_reply_to_screen_name != "" else False
            # Retweets start with "RT ..."
            retweet_status = True if tweet.text[0:3] == "RT " else False

            # Get info specific to the current tweet of the current user.
            tweet_info = [tweet.created_at.year,
                          tweet.created_at.month,
                          tweet.created_at.day,
                          tweet.created_at.hour,
                          unidecode(tweet.text),
                          lat,
                          long,
                          tweet.source,
                          tweet.in_reply_to_screen_name,
                          direct_reply,
                          retweet_status,
                          tweet.retweet_count,
                          tweet.favorite_count]

            # Below entities are stored as variable-length dictionaries, if present.
            hashtags = []
            hashtags_data = tweet.entities.get('hashtags', None)
            if(hashtags_data != None):
                for i in range(len(hashtags_data)):
                    hashtags.append(unidecode(hashtags_data[i]['text']))

            urls = []
            urls_data = tweet.entities.get('urls', None)
            if(urls_data != None):
                for i in range(len(urls_data)):
                    urls.append(unidecode(urls_data[i]['url']))

            user_mentions = []
            user_mentions_data = tweet.entities.get('user_mentions', None)
            if(user_mentions_data != None):
                for i in range(len(user_mentions_data)):
                    user_mentions.append(unidecode(user_mentions_data[i]['screen_name']))

            media = []
            media_data = tweet.entities.get('media', None)
            if(media_data != None):
                for i in range(len(media_data)):
                    media.append(unidecode(media_data[i]['type']))

            contributors = []
            if(tweet.contributors != None):
                for contributor in tweet.contributors:
                    contributors.append(unidecode(contributor['screen_name']))

            more_tweet_info = [', '.join(hashtags),
                               len(hashtags),
                               ', '.join(urls),
                               len(urls),
                               ', '.join(user_mentions),
                               len(user_mentions),
                               ', '.join(media),
                               ', '.join(contributors)]

            # Write data to CSV.
            writer.writerow(user_info + tweet_info + more_tweet_info)

        # Show progress.
        print("Wrote tweets by %s to CSV." % user)