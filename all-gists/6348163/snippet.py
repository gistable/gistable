from datetime import datetime
import urllib2
import urllib
import json
import os

def ajaxRequest(url=None):
	"""
	Makes an ajax get request.
	url - endpoint(string)
	"""
	req = urllib2.Request(url)
	f = urllib2.urlopen(req)
	response = f.read()
	f.close()
	return response	

access_token = os.getenv("access_token")

# ask for hashtag name
hashtag = raw_input("What hashtag would you like to download photos of? ")

# url to query for pictures
nextUrl = "https://api.instagram.com/v1/tags/"+hashtag+"/media/recent?access_token="+access_token
print nextUrl
# while there is a next url to go to
while nextUrl:
	# request the data at that endpoint 
	instagramJSON = ajaxRequest(nextUrl)
	instagramDict = json.loads(instagramJSON)
	# get new  nextUrl
	nextUrl = instagramDict["pagination"]["next_url"]
	instagramData = instagramDict["data"]
	# for every picture
	for picDict in instagramData:
		# get the image url and current time
		print picDict
		image = picDict["images"]["standard_resolution"]
		imageUrl = image["url"]
		print image
		time = str(datetime.now())
		# download the photo and save it
		urllib.urlretrieve(imageUrl, time+".jpg")