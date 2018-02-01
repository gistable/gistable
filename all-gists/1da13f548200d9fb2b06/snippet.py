#!/usr/bin/env python

# Requires this font : http://www.fonts2u.com/highvoltage.font
# The images are saved in a folder named by the subreddit name
# External Libraries : praw, PIL

import praw
import Image
import ImageDraw, ImageFont
import textwrap
import os

wrapify = lambda c, w: textwrap.wrap(c, width=w)

def getSubreddit(sub, limit=10):

	r = praw.Reddit(user_agent="RedditImagify")
	j = r.get_subreddit(sub).get_hot(limit=limit)
	
	content = [(x.title, x.selftext, x.short_link, sub) for x in j]

	return content

def mkimg(content, maxHeight=500):

	img  = Image.new("RGB", (500, maxHeight))
	tfont = ImageFont.truetype("HighVoltage.ttf", 36)
	bfont = ImageFont.truetype("HighVoltage.ttf", 20)
	draw = ImageDraw.Draw(img)

	draw.rectangle((0, 0, 500, maxHeight), fill=(255, 255, 255))
	
	y = 0
	for t in wrapify(content[0], 30):
		draw.text((20, 40+y), t, (0, 0, 0), font=tfont)
		y += 40
	
	y += 30

	for b in wrapify(content[1], 58):
		draw.text((20, 30+y), b, (0, 0, 0), font=bfont)
		y += 27
	
	if y>(maxHeight-100):
		mkimg(content, maxHeight+36)
		return None	
	
	print "[*] Saving %s"%content[2]
	img.save("%s/%s.png"%(content[3], content[2].lstrip("http://redd.it/")))

if __name__=="__main__":
	sub = raw_input("Enter the subreddit to fetch : ")
	if not os.path.exists(sub):
		os.mkdir(sub)
	n = int(raw_input("Enter no of post to fetch : "))
	for j in getSubreddit(sub, n):
		mkimg(j)
		
