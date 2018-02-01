import oauth2 as oauth
# OAuth2 python egg from : http://pypi.python.org/pypi/oauth2/1.5.170
# Install command : sudo easy_install oauth2
# Codebase : http://github.com/simplegeo/python-oauth2

# OAuth library in your favorite programming language : http://oauth.net/code/

import urllib
# URL encoding utilities

import sys,traceback
# Utilities for dealing with exception traces.

c_key = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX';  # your consumer key here
c_secret = 'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY';   # your secret key here

consumer = oauth.Consumer(key=c_key,secret=c_secret)
client = oauth.Client(consumer)
# Started a new OAuth consumer client

url = "http://qa.generalsentiment.com:8080/api/v1.php/globalTrendingTopics"
# REST URL pointing to the requisite API call , in this case "globalTrendingTopics" :

params = {"src": "all_internet", "trending_period": "trending_for_the_month", "result_count":"500", "date" : "201106"}
# Call parameters : 
# All parameters are required , unless specified.
#
# trending_period :       Essentially the length of the time period over which returned topics were trending.
#	         Possible values : "trending_for_the_day" , "trending_for_the_month" , "trending_for_the_year" .
#          Default : "trending_for_the_day"
# 
# date : Specifies trending time-point. Can be "yyyy" ( when trending_period = "trending_for_the_year" ) 
#                                           or "yyyymm" ( when trending_period = "trending_for_the_month" )
#                                           or "yyyymmdd" ( when trending_period = "trending_for_the_day" )
# 			  date should be between the years 1500 and 2500 (inclusive). 
#         Optional parameter. Default is either the date for yesterday , last month or last year depending on the value of "trending_period"
#			  
#
# src :       Optional parameter. Specifies monitored source.
#			  Possible values:
#			  "all_internet" : Everything we track.
# 			  "news" : News media and articles from online news sources.
#			  "twitter" : Twitter posts and feeds.
#			  "social" : Miscellaneous social media sources incl. blogs
#			  All other values are ignored and the default is used instead.
#			  Default value is "all_internet"
#
# result_count :  Places an upper limit on the number of trending topics returned. Default is 50, can go up to 500.

r_method= "POST"
# Request method is HTTP POST via OAuth.

try:
	r_body = urllib.urlencode(params,doseq=True).replace('+','%20')
	response,content = client.request(url,method=r_method,body=r_body)
	# Perform the request and get the response.
	print content
        # The output is a JSON list of objects , each corresponding to a trending entity / topic.
        # Each JSON object contains the following fields :
        # "entity" : The trending entity / topic.
        # "frequency" : Number of mentions of that entity during the time period.
        # "zscore" : The Z-score of an entity / topic , is the
				#		number of standard deviations that topic is away , during the
				#		trending time period , from its mean frequency over equivalent
				#		time periods , going back over all time.
        
except Exception as e:
	exc_type, exc_value, exc_traceback = sys.exc_info()
	sys.stderr.write('\nCaught exception '+type(e).__name__ + str(e.args) + '\n'.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
	# Get and print exception info and stack trace.
	#
	# Error code 603 : Missing mandatory parameters.
        # Error code 601 : Error in parameter entry (faulty data entry). The "error_message" field describes what was entered wrongly.
        # Error code 602 : Server contains no data for query.
        # Error code 500 : Internal server error occurred while processing query.