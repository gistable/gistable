from Queue import Queue			# Threadsafe queue for threads to use
from collections import Counter    	# To count stuff for us
import datetime                    	# Because datetime printing is hard
from pprint import pprint
import time                    		# Should be obvious
import subprocess                	# Used to send notifications on mac
import sys                    		# Get system info
import threading 			# Should be obvious
import json                             # Also obvious

# FB API wrapper ("pip install facebook-sdk")
import facebook

__author__ = 'Henri Sweers'

appeared = dict()


# For printing pretty colors in terminal
class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


# If you're on mac, install terminal-notifier ("brew install terminal-notifier")
#   to get nifty notifications when it's done
def notify_mac():
    if sys.platform == "darwin":
        try:
            subprocess.call(
                ["terminal-notifier", "-message", "Done", "-title", "FB_Bot",
                 "-sound", "default"])
        except OSError:
            print "If you have terminal-notifier, this would be a notification"


# Log message with colors
# ... I never learned the proper way to log in python
def log(message, *colorargs):
    if len(colorargs) > 0:
        print colorargs[0] + message + color.END
    else:
        print message


# Junk method used for testing
def test():
    log("Test")


# Export method, recieves a jsonObj of style {"label": dictionary}
def exportData(jsonDict):
    # Do stuff
    print "Exported"
    # print jsonDict


# Thread class. Each thread gets all the data from a certain date range
class RequestThread(threading.Thread):

    def __init__(self, queue, apikey, query, curr_time, num_weeks):

        # Super class
        threading.Thread.__init__(self)

        # Queue object given from outside. Queues are threadsafe
        self.queue = queue

        # Graph object for our call, authenticated with a token
        self.graph = facebook.GraphAPI(apikey)

        # FQL query with specified date range
        self.input_query = query

        # Counters. t-total, p-posts, c-comments
        self.tcounter = Counter()
        self.pcounter = Counter()
        self.ccounter = Counter()
        self.tpcounter = Counter()
        self.tccounter = Counter()
        self.cccounter = Counter()

        # Time range, for logging
        self.time_range = datetime.datetime.fromtimestamp(
            curr_time - num_weeks).strftime('%Y-%m-%d') + "-" + \
            datetime.datetime.fromtimestamp(curr_time).strftime(
                '%Y-%m-%d')

    # Main runner
    def run(self):

        log("\t(" + self.time_range + ') - Getting posts...')

        # Get group posts
        try:
            group_posts = self.graph.fql(query=self.input_query)
        except facebook.GraphAPIError as e:
            # 99% of the time this is just an expired API access token
            log("Error: " + str(e), color.RED)
            sys.exit()

        log("\t(" + self.time_range + ") - " +
            str(len(group_posts)) + " posts")

        # Iterate over posts
        if len(group_posts) != 0:
            for post in group_posts:
                comments_query = \
                    "SELECT fromid, likes, id, time FROM comment WHERE post_id="

                # If it's a new actor
                if post['actor_id'] in appeared.keys():
                    if appeared[post['actor_id']] > int(post['created_time']):
                        appeared[post['actor_id']] = int(post['created_time'])
                else:
                    appeared[post['actor_id']] = int(post['created_time'])

                # Add post's like count to that user in our total_likes_counter
                self.tcounter[post['actor_id']] += post[
                    'like_info']['like_count']

                # Add to top like posts counter
                self.pcounter[post['post_id']] = post['like_info'][
                    'like_count']

                # Timestamp of post by 
                day_timestamp = datetime.datetime.fromtimestamp(int(post['created_time']))
                day_timestamp = day_timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
                day_timestamp = (day_timestamp - datetime.datetime(1970, 1, 1)).total_seconds()

                # Add to post count
                self.tpcounter[str(day_timestamp)] += 1

                # Initialize controversial counter
                self.cccounter[post['post_id']] += 1

                # Get likes on comments
                comments = self.graph.fql(
                    comments_query + "\"" + str(post['post_id']) +
                    "\" LIMIT 350")

                # Iterate over comments
                if len(comments) != 0:
                    log("\t(" + self.time_range + ") - " + str(
                        len(comments)) + " comments")
                    log("\t(" + self.time_range + ') - Getting comments...')

                    for c in comments:
                        # add their like counts to their respective users
                        # in our total_likes_counter
                        self.tcounter[c['fromid']] += c['likes']

                        # add like count to top_comments_likes_counter
                        self.ccounter[c['id']] = c['likes']

                        # Add to comment count
                        self.tccounter[str(day_timestamp)] += 1

                        # Add to controversial counter
                        self.cccounter[post['post_id']] += 1

                        # If it's a new actor
                        if c['fromid'] in appeared.keys():
                            if appeared[c['fromid']] > int(c['time']):
                                appeared[c['fromid']] = int(c['time'])
                        else:
                            appeared[c['fromid']] = int(c['time'])

                else:
                    log("\tNo comments from this post")
        else:
            log("\tNo posts from this time frame")

        self.queue.put({'t': self.tcounter, 'p': self.pcounter, 'c':
                        self.ccounter, 'tp': self.tpcounter, 
                        'tc': self.tccounter, 'cc': self.cccounter})


# Method for counting various total likes in a group
def count_group_likes():
    # Access token can be obtained by doing the following:
    # - Log into facebook
    # - Go to this url: https://developers.facebook.com/tools/explorer
    fb_API_access_token = "token_goes_here"

    # Only necessary if you want to get an extended access token
    # You'll have to make a facebook app and generate a token with it
    # You'll also need to get the following two values from it
    fb_app_id = "id_goes_here"
    fb_secret_key = "key_goes_here"

    # Counter object to do the counting for us
    total_likes_counter = Counter()
    top_liked_posts_counter = Counter()
    top_liked_comments_counter = Counter()
    total_posts_counter = Counter()
    total_comments_counter = Counter()
    most_discussed_counter = Counter()

    group_id = "id_goes_here"        # Unique ID of the group to search.
    num_of_items_to_return = 30      # Return the top ____ most liked ____

    # Put the number of weeks you want it to increment by each time
    #   smaller is better, but too small and you could hit your rate limit
    #       ... which is 600 calls per 600 seconds. Maybe apps get more
    num_weeks = int("2")

    # Convert to unix time
    num_weeks_unix = num_weeks * 604800

    # Start date, in unix time (our group was made 2/13/12)
    # You can use this to convert: http://goo.gl/4QMFbW
    start_date = int("start_date_goes_here")

    datetime_start_date = datetime.datetime.fromtimestamp(start_date)

    # Query strings for FQL
    posts_query = \
        "SELECT post_id, like_info, actor_id, created_time FROM stream" + \
        " WHERE source_id=" + group_id + " AND created_time<"
    person_query = "SELECT first_name, last_name FROM user WHERE uid="

    # Authorize our API wrapper
    graph = facebook.GraphAPI(fb_API_access_token)

    # Code to programatically extend key
    if extend_key:
        result = graph.extend_access_token(fb_app_id, fb_secret_key)
        new_token = result['access_token']
        new_time = int(result['expires']) + time.time()

        # This will print out new extended token and new expiration date
        # Copy them and replace your token above with this one
        print 'New token: ' + new_token
        print 'New expiration date: ' + datetime.datetime.fromtimestamp(
            new_time).strftime('%Y-%m-%d %H:%M:%S')

    log('Getting group posts', color.BLUE)

    # Send end time to current time and work backward
    end_time = int(time.time())

    # Or manually set end time
    # end_time = <end_time>

    log('Current date is: ' + datetime.datetime.fromtimestamp(
        end_time).strftime('%Y-%m-%d'))

    log('Incrementing by ' + str(num_weeks) + ' weeks at a time')

    # List of thread objects
    threads = []

    # Threadsafe queue for the threads to dump their data in
    final_queue = Queue()

    log("Initializing threads...", color.BLUE)

    # While loop that creates the threads
    # Instantiates each thread with calculated time, keeps decrementing to
    # start
    while end_time > start_date:

        # New query
        new_query = posts_query + str(
            end_time) + " AND created_time>" + \
            str(end_time - num_weeks_unix) + " LIMIT 600"

        # Thread creation
        t = RequestThread(final_queue, fb_API_access_token, new_query,
                          end_time, num_weeks_unix)

        # Add it to our list
        threads.append(t)

        # Decrement the time
        end_time -= num_weeks_unix

        # Start the thread
        t.start()

    log("Joining threads...", color.BLUE)

    # Wait for all the threads to finish before counting everything up
    for t in threads:
        t.join()

    log("Done, merging data...", color.BLUE)

    # Count up all the data by merging all the counters from each thread result
    for stuff in list(final_queue.queue):
        total_likes_counter += stuff['t']
        top_liked_posts_counter += stuff['p']
        top_liked_comments_counter += stuff['c']
        total_posts_counter += stuff['tp']
        total_comments_counter += stuff['tc']
        most_discussed_counter += stuff['cc']

    most_active_day_counter = total_posts_counter + total_comments_counter

    # Returns key-value list of most liked people
    most_common_people = total_likes_counter.most_common(
        num_of_items_to_return)
    top_posts = top_liked_posts_counter.most_common(num_of_items_to_return)
    top_comments = top_liked_comments_counter.most_common(
        num_of_items_to_return)
    total_posts = total_posts_counter.most_common(num_of_items_to_return)
    total_comments = total_comments_counter.most_common(num_of_items_to_return)
    most_active_days = most_active_day_counter.most_common(num_of_items_to_return)
    most_discussed = most_discussed_counter.most_common(num_of_items_to_return)


    top_people_stats = []
    # Iterate over top people and retrieve names from their ID's
    # Use enumerate to keep track of indices for rank numbers
    log('\nPeople Stats', color.BOLD)
    log("* = Weighted average calc'd from user's first post date")
    for i, x in enumerate(most_common_people):
        person = graph.fql(person_query + str(x[0]))[0]

        now = datetime.datetime.now()
        join_date = datetime.datetime.fromtimestamp(appeared[x[0]])
        diff1 = now - datetime_start_date
        diff2 = now - join_date

        avg = x[1] / (diff1.total_seconds()/60/60/24/7)
        weighted_avg = x[1] / (diff2.total_seconds()/60/60/24/7)

        top_people_stats.append({
            "name": person['first_name'] + " " + person['last_name'],
            "likes": x[1],
            "avg": avg,
            "augmented_avg": weighted_avg,
            "first": int((join_date - datetime.datetime(1970, 1, 1)).total_seconds())
        })

        print '#' + str(i+1) + '. ' + person['first_name'] + " " + person['last_name']
        print '-- Likes: ' + str(x[1])
        print '-- Weekly average: ' + str(avg)
        print '-- Weekly average*: ' + str(weighted_avg)
        print '-- First post: ' + join_date.strftime('%Y-%m-%d')

    # Iterate over top posts and get info
    log('\nTop posts!', color.BOLD)
    for x in top_posts:
        post = graph.get_object(str(x[0]))
        s = str(x[1]) + " - " + post['from']['name'] + " - " + post['type']
        print s
        if 'message' in post:
            m = str(post['message'].encode('ascii', 'ignore')).replace('\n', ' ')
            if len(m) > 70:
                print '-- ' + m[0:70] + "..."
            else:
                print '-- ' + m
        print '-- http://www.facebook.com/' + post['id']

    # Iterate over top comments and get info
    log('\nTop comments!', color.BOLD)
    for x in top_comments:
        comment = graph.get_object(str(x[0]))
        s = str(x[1]) + " - " + comment['from']['name']
        print s
        if 'message' in comment:
            c = str(comment['message'].encode('ascii', 'ignore')).replace('\n', ' ')
            if len(c) > 70:
                print '-- ' + c[0:70] + "..."
            else:
                print '-- ' + c
        print '-- http://www.facebook.com/' + comment['id']

    # Iterate over total posts/comments and calculate info
    log('\nMost active days (by number of posts and comments)', color.BOLD)
    for x in most_active_days:
        d = datetime.datetime.fromtimestamp(float(x[0])).strftime('%m/%d/%Y')
        print str(x[1]) + " - " + d

    # Iterate over total posts and calculate info
    log('\nMost active days (by number of posts)', color.BOLD)
    for x in total_posts:
        d = datetime.datetime.fromtimestamp(float(x[0])).strftime('%m/%d/%Y')
        print str(x[1]) + " - " + d

    # Iterate over total comments and calculate info
    log('\nMost active days (by number of comments)', color.BOLD)
    for x in total_comments:
        d = datetime.datetime.fromtimestamp(float(x[0])).strftime('%m/%d/%Y')
        print str(x[1]) + " - " + d

    # Iterate over top posts and get info
    log('\nMost discussed', color.BOLD)
    for x in most_discussed:
        post = graph.get_object(str(x[0]))
        s = str(x[1]) + " - " + post['from']['name'] + " - " + post['type']
        print s
        if 'message' in post:
            m = str(post['message'].encode('ascii', 'ignore')).replace('\n', ' ')
            if len(m) > 70:
                print '-- ' + m[0:70] + "..."
            else:
                print '-- ' + m
        print '-- http://www.facebook.com/' + post['id']

    log('\nExporting...', color.BLUE)
    dataDict = json.dumps({"top_people_stats": top_people_stats,
                "top_liked_posts_counter": top_liked_posts_counter,
                "top_liked_comments_counter": top_liked_comments_counter,
                "total_posts_counter": total_posts_counter,
                "total_comments_counter": total_comments_counter,
                "most_active_day_counter": most_active_day_counter,
                "most_common_people": most_common_people,
                "top_posts": top_posts,
                "top_comments": top_comments,
                "total_posts": total_posts,
                "total_comments": total_comments,
                "most_active_days": most_active_days})

    exportData(dataDict)


args = sys.argv

extend_key = False          # boolean for if we want to extend token access

if len(args) > 1:
    if "--extend" in args:  # Pass in flag
        extend_key = True
    if "test" in args:
        test()
        sys.exit()
    else:
        log('No args specified')

count_group_likes()
notify_mac()
