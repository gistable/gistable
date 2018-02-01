# Author: chowmean
# simple python script to get the comment of youtube videos using google apis get method
# Date: 23:08:2015
# mail: gaurav.dev.iiitm@gmail.com	
# github:github.com/chowmean
#


import oauth2
import time
import urllib2
import json
import requests

url= "https://www.googleapis.com/youtube/v3/videos"
params=dict()


api_key='Yourapikey'
videoId='pxofwuWTs7c'

params["part"] = "snippet"      #mandatory
params["maxResults"] = "50"        #optional
params["textFormat"] = "plainText"  #or html
params["id"] = videoId     

params["key"] = api_key
url=url+'?'
i=0
for key,value in params.iteritems():
	if i==0:
		url=url+key+'='+value
		i=i+1
	else:
		url=url+'&'+key+'='+value
print url
resp=requests.get(url)
print resp.content