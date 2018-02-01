import requests
import json
from urlparse import urlparse

sip_domain = "SIP_DOMAIN.COM"
username = "USERNAME@SIP_DOMAIN.COM"
password = "YOUR_LYNC_PASSWORD"

def extractAuthURL(str):
    start = str.find('MsRtcOAuth');
    q1 = str.find('"',start);
    q2 = str.find('"',q1+1);
    if q1 == -1 or q2 == -1:
        raise Exception("cannot find auth string")
    return str[q1+1:q2]
#
# Lookup discoverry URL to determine user/auth url, hardcoded to internal. change to lyncdiscover for external users
#    
discover_url = "https://lyncdiscoverinternal.{0}/".format(sip_domain)
print "--1. GET: {0}".format(discover_url);
r1 = requests.get(discover_url)
print "--Response Code: {0}".format(r1.status_code)
j = r1.json();
user_url = j['_links']['user']['href']

#
# ping the user url, expect a 401/address of oath server
#
print "--2. GET: {0}".format(user_url);
r2 = requests.get(user_url);
print "--Response Code: {0}".format(r2.status_code)
auth_url = extractAuthURL(r2.headers['www-authenticate'])

#
# send auth request, expect 200/authentication token
#
r3_data = {'grant_type':'password', 'username':username,'password':password}
print "--3. POST: {0}".format(auth_url)
r3 = requests.post(auth_url,data=r3_data)
print "--Response Code: {0}".format(r3.status_code)
access_token = r3.json()

#
# resend user request w/ oath headers, look for applications url
#
auth_headers = {'Authorization':"{0} {1}".format(access_token['token_type'],access_token['access_token'])}
print "--4. GET: {0}".format(user_url)
r4 = requests.get(user_url,headers=auth_headers)
print "--Response Code: {0}".format(r4.status_code)

#
# create an application endpoint, takes a json query w/ app identifier and appropriate content type
#
application_data = {'culture':'en-us','endpointId':'1235637','userAgent':'pythonApp/1.0 (CritterOS)'}
applications_url=r4.json()['_links']['applications']['href']
print "--5. GET: {0}".format(applications_url)
r5_headers = {'content-type': 'application/json'}
r5_headers.update(auth_headers)
r5 = requests.post(applications_url,headers=r5_headers,data=json.dumps(application_data))
print "--Response Code: {0}".format(r5.status_code)
apps = r5.json()
#print json.dumps(r5.json(),indent=4)
up = urlparse(applications_url)
application_base = "{0}://{1}".format(up.scheme,up.netloc)

#
# invoke a plain GET to the myContacts url we found above. 
#
r6_url = application_base + apps['_embedded']['people']['_links']['myContacts']['href']
print "--6. GET: {0}".format(r6_url)
r6 = requests.get(r6_url,headers=auth_headers)
print "--Response Code: {0}".format(r6.status_code)
#print json.dumps(r6.json(),indent=4)
for contact in r6.json()['_embedded']['contact']:
    print "Name " + contact['name']