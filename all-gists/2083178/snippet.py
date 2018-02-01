"""
# Dump your data from Posterous.

Requires:

    * Posterous username and password
    * An API Token from http://posterous.com/api
    * Posterous site id also from http://posterous.com/api
    * The Python libraries requests and python-dateutil

To use:

    python posterous_dump.py

"""


API_TOKEN = '<api_token>'

USERNAME = '<username>'
PASSWORD = '<password>'

SITE_ID = '<side_id>'

POSTS_URL = 'http://posterous.com/api/2/sites/%s/posts' % (SITE_ID,)



FOLDER = 'posterous_dump'

import json, requests, os
from dateutil import parser


def fetchFromPosterous(page):
    print 'Fetching page %s' % (page,)
    result = requests.get(POSTS_URL, params={
        'api_token': API_TOKEN,
        'page': page,
    }, auth=(USERNAME, PASSWORD))
    print result.status_code
    return result.content

def savePosts(posts):
    print 'saving posts:', len(posts)
    for post in posts:
        savePost(post)
    if len(posts) == 0:
        raise

def savePost(post_json):
    print post_json
    print 'saving', post_json.get('slug')
    post_date = parser.parse(post_json.get('display_date'))
    post_folder = '%s-%s' % (post_date.strftime('%Y-%m-%d-%H-%M-%S'),post_json.get('slug'))
    target_dir = os.path.join(FOLDER, post_folder)
    print target_dir
    try:
        os.mkdir(target_dir)
    except OSError:
        pass
    file(os.path.join(target_dir,'post.json'),'w').write(json.dumps(post_json))
    getMedia(post_json['media'], target_dir)

def getMedia(media, target_dir):
    print len(media)
    files_to_get = []
    for image in media.get('images'):
        fetch_url = image.get('full').get('url')
        files_to_get.append(fetch_url)
    for video in media.get('videos'):
        files_to_get.append(video.get('url'))
        files_to_get.append(video.get('mp4'))
    for audio in media.get('audio_files'):
        files_to_get.append(audio.get('url'))

    for fetch_url in files_to_get:
        file_name = os.path.split(fetch_url)[1]
        out_file = requests.get(fetch_url)
        print out_file.status_code, file_name
        file(os.path.join(target_dir,file_name),'w').write(out_file.content)



page_to_fetch = 1

print 'Starting'

if not os.path.exists(FOLDER):
    os.mkdir(FOLDER)

while page_to_fetch:
    result = fetchFromPosterous(page_to_fetch)
    try:
        posts = json.loads(result)
    except ValueError:
        print raw_json_data
        page_to_fetch = None
    else:
        if len(posts) > 0 and result:
            savePosts(posts)
            page_to_fetch += 1
        else:
            page_to_fetch = None

    import time
    time.sleep(5)


print 'Done'
