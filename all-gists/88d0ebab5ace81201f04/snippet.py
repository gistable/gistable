import facebook
from collections import Counter
import requests

likes_counter = Counter()

# Get temp tokens at: https://developers.facebook.com/tools/explorer/ 
USER_ACCESS_TOKEN = ""

client = facebook.GraphAPI(access_token=USER_ACCESS_TOKEN, version='2.5')

URL = "/me/feed"
PAGE_COUNT = 0
POSTS_COUNT = 0

while True:

    PAGE_COUNT = PAGE_COUNT + 1

    if PAGE_COUNT > 100:
        break

    print("Page: {}".format(PAGE_COUNT))

    if PAGE_COUNT > 1:
        feed = requests.get(URL).json()
    else:
        feed = client.request(URL)

    try:
        if 'next' in feed['paging'].keys():
            URL = feed['paging']['next']
        else:
            break
    except:
        print(feed)

    posts = feed.get('data')
    if posts:
        for post in posts:
            POSTS_COUNT = POSTS_COUNT + 1
            if post.get('likes'):
                likes = post['likes']['data']
                post_likes = {}
                for like in likes:
                    post_likes[like['name']] = 1
                likes_counter.update(post_likes)
            else:
                print(post)
    else:
        print(feed)

top_likers = likes_counter.most_common(20)

print("TOTAL POSTS: {}".format(POSTS_COUNT))
for counter in top_likers:
    name = counter[0]
    percent = float((counter[1] / POSTS_COUNT) * 100)
    print("{0} - {1:.2f} %".format(name, percent))
