import requests
import time
import json


headers = {'User-Agent': 'android:subgrowth:v0.1 (by /u/twelvis)'}

def getit(subreddit):
    r = requests.get(
        'http://www.reddit.com/r/' +
        subreddit.strip() +
        '/about.json', timeout=30, headers=headers)
    if 200 != r.status_code:
        pass
    try:
        block = json.loads(r.text)
    except Exception as ex:
        print ex
        return False
    return block

def subinfo(subreddit):
    j = getit(subreddit)
    print j
    if j['data']:
        readers = j['data']['subscribers']
        active = j['data']['accounts_active']

        # construct the json object
        values = {'timestamp': int(time.time()),
                'readers': readers,
                'active': active,
                'sub': subreddit
                }
        return json.dumps(values)
    else:
        pass

if __name__ == '__main__':
    while True:
        print subinfo('dataisbeautiful')
        time.sleep(300) # sleep tight in seconds


# track multiple subs
# if __name__ == '__main__':
#     subs = ['dataisbeautiful',
#             'entrepreneur',
#             'seo']

#     while True:
#         time.sleep(300)
#         for sub in subs:
#             print subinfo(sub)
