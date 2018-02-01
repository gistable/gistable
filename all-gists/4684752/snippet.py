#Sorry, in April 30, 2015, with Facebook 2.0 API update only friends that use the app will be show
import urllib.request
import json

def save_image(friend):
  size = '/picture?width=200&height=200'
  url = 'https://graph.facebook.com/'+ friend['id'] + size
  image = urllib.request.urlopen(url).read()
  f = open(friend['name'] + '.jpg', 'wb')
  f.write(image)
  f.close()
  print (friend['name'] + '.jpg impresso')
#get the token https://developers.facebook.com/tools/explorer
url = 'https://graph.facebook.com/me/friends?access_token=EAACEdEose0cBAD5XZCz5JXYvqyeJzcSvFZC42toHiWyfjhcZCMZBZCpE3uRJnEBsrhUEMRK1wWs6SsdiDFxsI1mYwyoNuMix2XZCpvsKbZB9TumtZBlcLeIpl4pa931Ce9rTinEAhtyVVZAAZAX4NmfpBUqWtzCRC0fX5GZBn7ZC28mPKAZDZD'
resp = urllib.request.urlopen(url).read()
data = json.loads(resp.decode('utf-8'))

for friend in data['data']:
  save_image(friend)

