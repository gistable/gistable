#!/usr/bin/python
#
#This class is primarily used for converting desktop and mobile links to Tweetbot URI format
#
#Example use:
#
#link = TwitterLink("https://twitter.com/binaryghost/statuses/259463759133814785")
#print(link.converted)
#
import re

class TwitterLink:
    def __init__(self, value):
        self.original = value
        self.isMobile = self.testForMobile()
        self.converted = self.convertLink()

    def testForMobile(self):
		match = re.finditer("http.*://.*mobile", self.original)
		if tuple(match):
			return True
		else:
			return False

    def convertLink(self):
        if self.isMobile:
            httpReplaced = re.sub("^http.*://.*mobile.twitter.com/", "tweetbot://", self.original)
            return re.sub("statuses", "status", httpReplaced)
        else:
            httpReplaced = re.sub("^http.*://.*twitter.com/", "tweetbot://", self.original)
            return re.sub("statuses", "status", httpReplaced)
