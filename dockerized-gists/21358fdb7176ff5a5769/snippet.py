import requests
import time
num = 0
user = "technoboy10"
key = "get your own! :P"
message = "event name here"

scratch = 'https://api.scratch.mit.edu/proxy/users/' + user + '/activity/count'
ifttt = 'https://maker.ifttt.com/trigger/' + message + '/with/key/' + key
while True:
    r = requests.get(scratch).json()['msg_count']
    if r != num and r != 0:
        num = r
        requests.get(ifttt, params={"value1":r})
    time.sleep(30)
