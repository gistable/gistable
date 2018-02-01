#!/usr/local/bin/python2.7

import datetime
import time
import re
import os
from twython import Twython
import sys
import traceback
import httplib, urllib #used in the Pushover code


#sys.stdout = open('twitter.log', 'a') #Outputs to file instead of Standard Output.

# Linux:
#folderPath = '/home/USERNAME/Dropbox/Scripts/Twitter/'
#folderAttach = '/home/USERNAME/Dropbox/Scripts/Twitter/attach/'

# Synology:
folderPath = '/SHARED_DRIVE/Dropbox/Scripts/Twitter/'
folderAttach = '/SHARED_DRIVE/Dropbox/Scripts/Twitter/attach/'

schFile = 'TweetSchedule.txt'

#Posts only if current time is within 50 min of predefined post time in text file.
#The script has been setup in the Synology to run every hour.
postInterval = 3000

# Twitter Credentials
App_Key='INCLUDE_YOURS_HERE'
App_Secret='INCLUDE_YOURS_HERE'
Oauth_Token='INCLUDE_YOURS_HERE'
Oauth_Token_Secret='INCLUDE_YOURS_HERE'


def pushover(msg):

    conn = httplib.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
        urllib.urlencode({
            "token": "'INCLUDE_YOURS_HERE'",
            "user": "'INCLUDE_YOURS_HERE'",
            "message": msg,
    }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()


def postTweets(tweetText, tweetAttach):

	twitter = Twython(App_Key, App_Secret, Oauth_Token, Oauth_Token_Secret)

	try: 

		if tweetAttach=='':
			
			twitter.update_status(status=tweetText)
			print 'Successfully tweeted!'
		
		else:
			completeAttPath = folderAttach+tweetAttach
			attachment=open(completeAttPath, 'rb')
			twitter.update_status_with_media(media=attachment, status=tweetText)
			attachment.close()

			print 'Successfully tweeted!'
		
	except:

		er = traceback.format_exc()
		print 'Warning: tweet -> '+tweetText+'<- could not be tweeted'
		print 'Error:\n'+er
		msg = 'Tweet: '+tweetText+'\nError: '+er[-180:]
		pushover(msg)
			
	return


def isItTime(freq): #receives string in the form XXX@XX:XX@XX:XX or XXXX-XX-XX@XX:XX@XX:XX per day
	
	now = datetime.datetime.now()
	postFlag = False

	days = freq.split(",")
	for day in days:

		rightDay = False
		times = day.split("@")
		
		# Determining if it is the correct date/week day:
		# ---
		
		#takes 1st item in the list - which is the date/week day - and determines which type of date it is:
		if re.match('^[0-9]{4}-[0-9]{2}-[0-9]{2}$',times[0]):
			print 'Processing date in xxxx-xx-xx format'
			
			if times[0]==now.strftime("%Y-%m-%d"):
				rightDay = True
				print 'It\'s the right day'

		elif re.match('^[a-zA-Z]{3}$',times[0]):
			print 'Processing date in XXX format'

			if times[0]==now.strftime("%a"): #Weekday's as local's abbreviated name: Mon, Tue, etc.
				rightDay = True
				print 'It\'s the right day'

		else:
			print times[0]+' -> Wrong date format!'

		
		# Determining if it is the correct time:
		# ---
		if rightDay:

			for time in times[1:]: #doesn't iterate over the 1st element which is the day
				if re.match('^[0-9]{1,2}:[0-9]{2}',time):

					nowStr = now.strftime("%H:%M") #Converts datetime object to string (so that it can be converted to a time object below)

					postTime = datetime.datetime.strptime(time,'%H:%M') #Converts the string into a time object
					nowTime = datetime.datetime.strptime(nowStr,'%H:%M') 
					diffTime = nowTime - postTime
					diffTimeSeconds = diffTime.total_seconds()

					if diffTimeSeconds>=0 and diffTimeSeconds<postInterval: 
						
						postFlag = True
						print 'It\'s the right time'

				else: 
					print time+' -> Wrong time format!'

	return postFlag


#Main Script

schTweets = open(folderPath+schFile,'rU') #IMPORTANT: rU Opens the file with Universal Newline Support, so \n and/or \r is recognized as a new line. 
tweetList = schTweets.readlines()
schTweets.close()

print '\n%s Running script...' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

for tweet in tweetList:
	tweet = tweet.strip('\n')
	
	try:
		tStatus, tText, tAttach, tTimes = tweet.split('|')
		if tStatus=='a':
			
			print 'Checking time interval '+tTimes
			if isItTime(tTimes):
				print 'Trying to post...'
				postTweet(tText, tAttach)
			else:
				print 'Not right time to tweet'
	
	except ValueError:
		print 'Incorrect line format. There might not be a | character in the line'
		pass

