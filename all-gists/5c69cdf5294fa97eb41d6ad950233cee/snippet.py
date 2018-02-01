#!/usr/bin/env python
# encoding: utf-8

"""
python 2.x
Scrape members from a Twitter list and then get their bios, locations, etc.
Based on 
https://github.com/lamthuyvo/social-media-data-scripts/blob/master/scripts/twitter_bio_info_compiler.py 
and 
https://github.com/kylemanna/social-utils/blob/master/twitter/list-follow.py 
"""

import tweepy # https://github.com/tweepy/tweepy
import csv
# import authentication credentials
from secrets import TWITTER_C_KEY, TWITTER_C_SECRET, TWITTER_A_KEY, TWITTER_A_SECRET

#authorize twitter, initialize tweepy
auth = tweepy.OAuthHandler(TWITTER_C_KEY, TWITTER_C_SECRET)
auth.set_access_token(TWITTER_A_KEY, TWITTER_A_SECRET)
api = tweepy.API(auth)

# which Twitter list and who owns it
slug = 'florida-legislators'
owner = 'JordanRaynor'


def get_list_members(api, owner, slug):
	members = []
	# without this you only get the first 20 list members
	for page in tweepy.Cursor(api.list_members, owner, slug).items():
		members.append(page)
	# create a list containing all usernames
    return [ m.screen_name for m in members ]


# create new CSV file and add column headings
def create_csv(filename, usernames):
	csvfile = open(filename, 'w')
	c = csv.writer(csvfile)
	# write the header row for CSV file
	c.writerow( [ "name",
				"display_name",
				"bio",
				"followers_count",
				"following_count",
				"acct_created",
				"location" ] )
	# add each member to the csv
	for name in usernames:
		user_info = get_userinfo(name)
		c.writerow( user_info )
	# close and save the CSV
	csvfile.close()

def get_userinfo(name):
	# get all user data via a Tweepy API call
	user = api.get_user(screen_name = name)
	# create row data as a list
	user_info = [ name.encode('utf-8'),
				user.name.encode('utf-8'),
				user.description.encode('utf-8'),
				user.followers_count,
				user.friends_count,
				user.created_at,
				user.location.encode('utf-8') ]
	# send that one row back
	return user_info

def main():
	# provide name for new CSV
	filename = "userinfo.csv"
	# create list of all members of the Twitter list
	usernames = get_list_members(api, owner, slug)
	# create new CSV and fill it
	create_csv(filename, usernames)
	# tell us how many we got
	print "Number of rows should be %d, plus the header row." % len(usernames)

if __name__ == '__main__':
	main()
