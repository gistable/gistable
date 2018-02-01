#Downloads all the images in a set, given the set id
# you need http://stuvel.eu/flickrapi#installation

import flickrapi
import urllib2
import os

api_key = 'a flickr API key'

#id of set you would like to download
set_id = '72157628308492421' 

flickr = flickrapi.FlickrAPI(api_key)
for photo in flickr.walk_set(set_id):
    
    farm_id = photo.get('farm')
    server_id = photo.get('server')
    photo_id = photo.get('id')
    photo_secret = photo.get('secret')
    
    #the 'b' at the end of url downloads in 1024x768. If you want originals, set this to 'o'.
    photo_url = "http://farm%s.staticflickr.com/%s/%s_%s_b.jpg" % (farm_id, server_id, photo_id, photo_secret)
    print photo_url
    
    opener1 = urllib2.build_opener()
    page = opener1.open(photo_url)
    photo = page.read()
    
    filename = photo_id + '.jpg'
    fout = open(filename, "wb")
    fout.write(photo)
    fout.close()
