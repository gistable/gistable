import requests
import json
import re

baseurl = "https://slack.com/api/channels.history"
token = "ur_token_plz"
channel = "C029WAA59"
urlregex = re.compile("<(http[s]{0,1}:\/\/.+?)>")

def scrapelinks(latest=""):
    payload = {"token"  : token,
               "channel": channel,
               "latest" : latest,
               "count"  : 1000
               }
    r = requests.get(baseurl, params=payload)
    j = json.loads(r.text)

    for m in j['messages']:
        if 'text' in m:
            mtch = urlregex.match(m['text'])
            if mtch:
                print(mtch.groups()[0])
        elif 'attachments' in m:
            for a in m['attachments']:
                print(urlregex.match(a['text']).groups()[0])

    if(j['has_more']):
       scrapelinks(latest=j['messages'][-1]['ts'])

scrapelinks()
