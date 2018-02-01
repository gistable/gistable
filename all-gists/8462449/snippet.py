import praw
import time

seen = []

def main():
	user_agent = ("User stalker 1.0")
	r = praw.Reddit(user_agent=user_agent)
	r.login('username', 'password')

	userName = "target"
	user = r.get_redditor(userName)

	
	while True:
		posts = user.get_submitted(limit=10) # set to whatever you want (1000 is the limit I think)

		print '[*] Posts'
		for thing in posts:
			if thing.id in seen:
				continue

			try:
				thing.add_comment('http://i.imgur.com/Y9o0p.png') # Change this
				seen.append(thing.id)
			except Exception, e:
				pass

		print '[*] Comments'
		comments = user.get_comments(limit=10) # set to whatever you want (1000 is the limit I think)

		for thing in comments:
			if thing.id in seen:
				continue

			try:
				thing.reply('http://i.imgur.com/Y9o0p.png') #Change this
				seen.append(thing.id)
			except Exception, e:
				pass

		print '[*] Sleeping'
		time.sleep(300) # sleep for ~5 minutes

	print '[*] done'


if __name__ == "__main__":
	main()