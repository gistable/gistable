import requests
from requests.auth import OAuth1
from oauthlib.oauth1.rfc5849 import SIGNATURE_RSA

client_key = u'...'

# You need to register your key with the OAuth provider first,
# in this case Google at https://accounts.google.com/ManageDomains
key = open("your_rsa_key.pem").read()

# Request token endpoint for access to Blogger
url = u'https://www.google.com/accounts/OAuthGetRequestToken?scope=https%3A%2F%2Fwww.blogger.com%2Ffeeds%2F'

queryoauth = OAuth1(client_key, signature_method=SIGNATURE_RSA,
                    rsa_key=key, signature_type='query')
headeroauth = OAuth1(client_key, signature_method=SIGNATURE_RSA,
                    rsa_key=key, signature_type='auth_header')
bodyoauth = OAuth1(client_key, signature_method=SIGNATURE_RSA,
                    rsa_key=key, signature_type='body')

r_query = requests.get(url, auth=queryoauth)
r_header = requests.get(url, auth=headeroauth)
r_body = requests.post(url, auth=bodyoauth)