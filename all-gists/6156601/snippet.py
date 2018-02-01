#!/usr/bin/python
import wolframalpha
import sys
#Get a free API key here http://products.wolframalpha.com/api/
#I may disable this key if I see lots of abuse
app_id='Q59EW4-7K8AHE858R'

client = wolframalpha.Client(app_id)

query = ' '.join(sys.argv[1:])
res = client.query(query)


print query

if len(res.pods) > 0:
    texts = ""
    pod = res.pods[1]
    if pod.text:
        texts = pod.text
    else:
        texts = "I have no answer for that"
    print texts
else:
    print "I am not sure"

