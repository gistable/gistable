import urllib
import json

response = urllib.urlopen("http://search.twitter.com/search.json?q=smu")
d = json.load(response)

print len(d.keys())
print d.keys()
print type(d["results"])
print len(d["results"])

for tweet in d["results"]:
    print tweet["from_user_name"], "wrote"
    print tweet["text"]
    print ""
