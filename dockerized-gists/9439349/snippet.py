import praw
import time
from collections import deque

r = praw.Reddit(user_agent = 'AMA_Notifier')
r.login()

cache = deque(maxlen = 200)

thisUser = raw_input("Please enter your reddit username\n")

url = raw_input("Please enter the URL of the AMA " + \
	"you would like to get notifications for:\n")

submission = r.get_submission(url)
author = submission.author
firstRun = True;

#Collects all replies that were already in AMA when program
def cacheOld(comments): 
	print "Caching Old  Replies"
	for comment in comments:
		replies = comment.replies
   		for reply in replies:
			if reply.id not in cache and reply.author == author:
				cache.append(reply.id)
	return False


print "Viewing Submission: " + submission.title
while True:
	comments = submission.comments
	if(firstRun):
		firstRun = cacheOld(comments)
	for comment in comments:
		replies = comment.replies
   		for reply in replies:
			if reply.id not in cache and reply.author == author:
				message = ("User " + author.name + " has just replied to a question in their AMA\n" +
					"\n\n**Question**: " + comment.body + "\n\n**Answer**: >" + reply.body + "\n\n**VIEW AT:** " + comment.permalink)
				r.send_message(thisUser, "AMA UPDATE", message)
				print "Message Sent :D"
				cache.append(reply.id)
	submission = r.get_submission(url)
	time.sleep(5)



