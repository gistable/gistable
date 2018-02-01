<<<<<<< Updated upstream
#!/usr/bin/python

import flickrapi # http://stuvel.eu/projects/flickrapi
import json as simplejson
import urllib2

api_key = ''
api_secret = ''
photoset_id = ''

def download(url):
	"""Copy the contents of a file from a given URL
	to a local file.
	"""
	import urllib
	webFile = urllib.urlopen(url)
	localFile = open(url.split('/')[-1], 'w')
	localFile.write(webFile.read())
	webFile.close()
	localFile.close()

flickr = flickrapi.FlickrAPI(api_key, api_secret,)

json = flickr.photosets_getPhotos(
           photoset_id=photoset_id,
           extras='original_format',
           format='json',
           nojsoncallback="1",
          )

photoset = simplejson.loads(json) # check it's valid JSON

for photo in photoset['photoset']['photo']:
  url = "http://farm%s.static.flickr.com/%s/%s_%s_o.jpg" % (photo['farm'], photo['server'], photo['id'], photo['originalsecret'])
  print url
  download(url)

=======
#!/usr/bin/python

import flickrapi # http://stuvel.eu/projects/flickrapi
import json
import urllib2

api_key = '41c2d61e53aa4183b07a556a22794462'
api_secret = 'b85cded078f12e73'
photoset_id = '72157629082469698'

def download(url):
    """Copy the contents of a file from a given URL
    to a local file.
    """
    import urllib
    webFile = urllib.urlopen(url)
    localFile = open(url.split('/')[-1], 'w')
    localFile.write(webFile.read())
    webFile.close()
    localFile.close()

flickr = flickrapi.FlickrAPI(api_key, api_secret,)

doc = flickr.photosets_getPhotos(
           photoset_id=photoset_id,
           extras='original_format',
           format='json',
           nojsoncallback="1",
          )

photoset = json.loads(doc) # check it's valid JSON

for photo in photoset['photoset']['photo']:
    url = "http://farm%s.static.flickr.com/%s/%s_%s_o.jpg" % (photo['farm'], photo['server'], photo['id'], photo['originalsecret'])
    print url
    download(url)

>>>>>>> Stashed changes
