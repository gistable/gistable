import httplib2
from apiclient.discovery import build
from oauth2client.client import AccessTokenCredentials

def connect_helper(user):
    c = user.social_auth.get(provider='google-oauth2')
    access_token = c.tokens['access_token']
 
    credentials = AccessTokenCredentials(access_token, 'my-user-agent/1.0')
    http = httplib2.Http()
    http = credentials.authorize(http)
    service = build(serviceName='calendar', version='v3', http=http,
           developerKey='...')
    
    return service
    