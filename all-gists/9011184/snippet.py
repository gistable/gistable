"""
fbfeed2csv: a tool to download all posts from a user/group/page's facebook feed to a csv file
yuzawa-san
https://github.com/yuzawa-san
"""

import json
import urllib2
import time
import csv
import re
import argparse



def loadPage(url):
    # delay
    time.sleep(1)
    # download
    response = urllib2.urlopen(url)
    content = response.read()
    payload = ''
    print "DOWNLOAD!"
    try:
        payload = json.loads(content)
    except:
        print "JSON decoding failed!"
    if 'data' in payload:
        out = []
        for post in payload['data']:
            if 'message' in post:
                # make timestamp pretty
                timestamp = post['created_time']
                timestamp = re.sub(r'\+\d+$', '', timestamp)
                timestamp = timestamp.replace('T',' ')
                out.append({
                    'author': post['from']['name'].encode('ascii', 'ignore'),
                    'timestamp': timestamp,
                    'message': post['message'].encode('ascii', 'ignore')})
        out2 = []
        if 'paging' in payload:
            out2 = loadPage(payload['paging']['next'])
        return out + out2
    return []
    

# entry point:

# get args
parser = argparse.ArgumentParser()
parser.add_argument('id', help='ID of Graph API resource')
parser.add_argument('-o', '--out', default="fbdump.csv", help='Output file')
parser.add_argument('-t', '--token', help='Authentication token')
args = parser.parse_args()

try:
    out = loadPage("https://graph.facebook.com/%s/feed?fields=from,message,created_time&limit=1000&access_token=%s" % (args.id, args.token))
    # write output to file
    f = open(args.out,'wb')
    w = csv.DictWriter(f,['author','timestamp','message'])
    w.writerows(out)
    f.close()
except urllib2.HTTPError as e:
    print "Download failed:",e
    error_message = e.read()
    print error_message
except KeyboardInterrupt:
    print "Canceled!"