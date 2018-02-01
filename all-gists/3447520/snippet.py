import httplib
import time
from hashlib import sha1
import random
import string
import json

callerId = "YOUR_CALLER_ID"
timestamp = str(int(time.time()))
unique = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(16))
hashstr = sha1(callerId+timestamp+"YOUR_PRIVATE_KEY"+unique).hexdigest()

url = "/listings?q=nacka&callerId="+callerId+"&time="+timestamp+"&unique="+unique+"&hash="+hashstr

connection = httplib.HTTPConnection("api.booli.se")
connection.request("GET", url)
response = connection.getresponse()
data = response.read()
connection.close()

if response.status != 200:
    print "fail"

result = data