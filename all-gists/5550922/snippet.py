import praw # simple interface to the reddit API, also handles rate limiting of requests
import re
from collections import deque 
from time import sleep

USERNAME  = "Your username here"
PASSWORD  = "Your password here"
USERAGENT = "Your useragent string here. It should include your /u/username as a courtesy to reddit"

r = praw.Reddit(USERAGENT)
r.login(USERNAME,PASSWORD) # necessary if your bot will talk to people

cache = deque(maxlen=200) # To make sure we don't duplicate effort

r_pat = re.compile(' r/[A-Za-z0-9]+')
u_pat = re.compile(' u/[A-Za-z0-9]+')

def check_condition(comment):
    text = comment.body    
    broken = set(re.findall(r_pat, text))
    broken.union( set(re.findall(u_pat, text)) )
    condition = False
    if broken:
        condition = True
    return condition, broken

def bot_action(c, links):
    text = ''
    for link in links:
        text += "/" + link[1:] + "\n"
    print c.author.name, c.subreddit.display_name, c.submission.title
    print text
    c.reply(text)

running = True
while running:    
    all = r.get_all_comments(limit = None, url_data = {'limit':100})
    for c in all:
        if c.id in cache:
            break
        cache.append(c.id)
        bot_condition_met, parsed = check_condition(c)
        if bot_condition_met:
            try:
                bot_action(c, parsed)
                
            except KeyboardInterrupt:
                running = False
            except praw.errors.APIException, e:
                print "[ERROR]:", e
                print "sleeping 30 sec"
                sleep(30)                
            except Exception, e: # In reality you don't want to just catch everything like this, but this is toy code.
                print "[ERROR]:", e
                print "blindly handling error"
                continue
