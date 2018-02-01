import urllib
import json
import string
import sys
import ConfigParser
import tweepy

def craftTweet(match_id, level, hero, kills, deaths, assists):
    unformatted = 'Just played a match: Hero: Lvl. {} {} K/D/A: {}/{}/{}\nDotabuff: {}'

    url = 'http://www.dotabuff.com/matches/' + match_id

    formatted = unformatted.format(level, hero, kills, deaths, assists, url)

    return formatted

def tweet(status):
    config = ConfigParser.RawConfigParser()
    config.read('dota2_tweet.cfg')
    
    # http://dev.twitter.com/apps/myappid
    CONSUMER_KEY = config.get('API Information', 'CONSUMER_KEY')
    CONSUMER_SECRET = config.get('API Information', 'CONSUMER_SECRET')
    # http://dev.twitter.com/apps/myappid/my_token
    ACCESS_TOKEN_KEY = config.get('API Information', 'ACCESS_TOKEN_KEY')
    ACCESS_TOKEN_SECRET = config.get('API Information', 'ACCESS_TOKEN_SECRET')

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    result = api.update_status(status)

url = 'https://api.steampowered.com/IEconDOTA2_570/GetHeroes/v0001/?key=<key>&language=en_us'

response = urllib.urlopen(url)
hero_json_obj = json.load(response)

account_id = '103637655'

args = {
    'key': '<key>',
    'format': 'JSON',
    'account_id': account_id,
    'matches_requested': '2',
}

encoded_args = urllib.urlencode(args)

url = 'http://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/V001/?' + encoded_args

response = urllib.urlopen(url)
json_obj = json.load(response)

match_id = json_obj['result']['matches'][0]['match_id']

# check if we already tweeted this match
config = ConfigParser.RawConfigParser()
config.read('dota2_tweet.cfg')

last_match = config.get('config', 'LAST_MATCH')

if str(match_id) == str(last_match):
    sys.exit('you already tweeted this match')

config.set('config', 'LAST_MATCH', match_id)
with open('dota2_tweet.cfg', 'w') as f:
    config.write(f)

args = {
    'key': '<key>',
    'format': 'JSON',
    'match_id': match_id,
}

encoded_args = urllib.urlencode(args)

url = 'http://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/V001/?' + encoded_args

response = urllib.urlopen(url)
json_obj = json.load(response)

my_player = {}
hero_string = ''

for player in json_obj['result']['players']:
    if str(player['account_id']) == account_id:
        my_player = player

for hero in hero_json_obj['result']['heroes']:
    if hero['id'] == my_player['hero_id']:
        hero_string = hero['localized_name']

tweet(craftTweet(
    str(json_obj['result']['match_id']),
    str(my_player['level']),
    hero_string,
    str(my_player['kills']),
    str(my_player['deaths']),
    str(my_player['assists'])
))