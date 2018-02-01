"""
Will pull images from a tag. 

I'm using this to make a photobook of my brother in law's wedding, 
but you might find it helpful for any number of other things.
"""
from instagram.client import InstagramAPI
from pprint import pprint
import urlparse
import urllib


access_token = "YOUR_TOKEN_HERE"
api = InstagramAPI(access_token=access_token)
max_tag_id = None
while True:
    tagged, next_url = api.tag_recent_media(tag_name="YOUR_TAG",
            count=10, max_tag_id=max_tag_id)
    for media in tagged:
        if media.type is 'video':
            continue
        if media.images.get('standard_resolution') is not None:
            filename = media.id + '.jpg'
            urllib.urlretrieve(media.images.get('standard_resolution').url, filename)
            print "Wrote to %s" % filename

    if next_url is None:
        break

    p = urlparse.urlparse(next_url)
    max_tag_id = urlparse.parse_qs(p.query)['max_tag_id'][0]
    print "\nNext page, starting with max_tag_id %s\n" % max_tag_id

print "\nDONE!\n"
