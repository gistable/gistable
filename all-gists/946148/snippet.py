import oauth2 as oauth
import urllib
def yam():
  	consumer_key = YOUR_CONSUMER_KEY
  	consumer_secret= YOUR_CONSUMER_SECRET
  	access_token = YOUR_ACCESS_TOKEN
  	access_token_secret = YOUR_ACCESS_TOKEN_SECRET
  	consumer = oauth.Consumer(consumer_key, consumer_secret)
  	token = oauth.Token(access_token,access_token_secret)
  	client = oauth.Client(consumer,token)
  	resource = 'https://www.yammer.com/api/v1/messages.json';
  	params = {'body': 'YOUR_MESSAGE_BODY'}
  	oauth_request = oauth.Request.from_consumer_and_token(consumer, token=token, http_method='POST', http_url=resource, parameters=params)
  	oauth_request.sign_request(oauth.SignatureMethod_HMAC_SHA1(), consumer, token)
  	response = client.request(resource,method="POST", headers={'Content-Type':'application/x-www-form-urlencoded'},body=urllib.urlencode(params))
  	print response