import tweepy
import matplotlib.pyplot as plt
from time import time
#number of statuses logged
status_count = 0

#set up auth
auth1 = tweepy.auth.OAuthHandler('Consumer Key','Consumer Secret')
auth1.set_access_token('Auth Key','Auth Secret')

#create the api
api = tweepy.API(auth1)

#STREAM CLASS
class StreamListener(tweepy.StreamListener):

	#these defs override the default ones
	def on_status(self, status):

		global status_count

		statustext = status.text
		
		#increment status_count
		status_count += 1.0
		
		#if it has been longer than 10 seconds
		time_now = time()
		if time_now - start_time > timeout_duration:
			#end stream
			return False


#create empty array to store calculated percents
percents = []

#how long to run the stream for each emotion
timeout_duration = 10
#times the stream has been run - aesthetic
time_run = 0
#times to run code
times_to_run = 20
#init average percentage
average_percentage = 0

#run x times
for c in range(0,times_to_run-1):
	time_run += 1
	print time_run

	#Get smile faces
	print "Gathering Smilies..."

	start_time = time()

	#create listener, start, and set filters
	l = StreamListener()
	streamer = tweepy.Stream(auth=auth1, listener=l, timeout = timeout_duration)
	setTerms = [':)', '(:', ':]', '[:']
	streamer.filter(None, setTerms)

	#when that finishes, set the happy_count equal to the number of statuses
	#and reset status_count
	happy_count = status_count
	status_count = 0


	print "Gathering Unhappy Faces..."

	start_time = time()

	#create lister2
	l2 = StreamListener()
	streamer2 = tweepy.Stream(auth=auth1, listener=l2, timeout= timeout_duration)
	setTerms2 = [':(','):',':[',']:']
	streamer2.filter(None, setTerms2)

	#set sad_count to number of logged statuses
	sad_count = status_count

	print "Happy: ", happy_count, "  Sad: ", sad_count
	percent = (happy_count/(happy_count+sad_count)) * 100.0
	print "Percentage Happy = ", percent

	percents.append(percent)


	average_percentage += percent


print "AVERAGE PERCENTAGE OF PEOPLE THAT ARE HAPPY: ", average_percentage/times_to_run

#write to file for posterity - overwritten each time the script is called
f = open('twitter_over_time.txt', 'w')
for per in percents:
	f.write(str(per))
	f.write("\n")
f.close()

#plot with matplotlib

plt.plot(percents)
plt.ylabel("Percent of Users with ':)' in Their Status")
plt.xlabel("Time in 20 Second Increments")
plt.show()
