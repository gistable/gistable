import base64, copy, sys
import requests
import json
from urlparse import urlparse

sip_domain = "company.com"
username = "firstname.lastname@company.com"
password = "somepassword"

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
discover_url = "https://lyncdiscover.{0}/".format(sip_domain)
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

headers = copy.copy(auth_headers)
headers["Content-Type"] = "application/json"

#
# create an application endpoint, takes a json query w/ app identifier and appropriate content type
#
application_data = {'culture':'en-us','endpointId':'1235637','userAgent':'lyncApp/1.4 (MacOSX)'}
applications_url=r4.json()['_links']['applications']['href']
print "--5. GET: {0}".format(applications_url)
r5_headers = {'content-type': 'application/json'}
r5_headers.update(auth_headers)
r5 = requests.post(applications_url,headers=r5_headers,data=json.dumps(application_data))
print "--Response Code: {0}".format(r5.status_code)
apps = r5.json()
# print json.dumps(r5.json(),indent=4)
up = urlparse(applications_url)
application_base = "{0}://{1}".format(up.scheme,up.netloc)

if 'makeMeAvailable' in apps['_embedded']['me']['_links']:
	# Put me online
	r6_url = application_base + apps['_embedded']['me']['_links']['makeMeAvailable']['href']
	print "--6. POST: {0}".format(r6_url)
	r6 = requests.post(r6_url,headers=headers, data=json.dumps({"SupportedModalities": ["Messaging"], "signInAs": "Online"}))
	print "--Response Code: {0}".format(r6.status_code)
# else:
# 	# Put me offline
# 	r7_url = application_base + apps['_links']['self']['href']
# 	print "--7. DELETE: {0}".format(r7_url)
# 	r7 = requests.delete(r7_url,headers=headers)
# 	print "--Response Code: {0}".format(r7.status_code)
# 	sys.exit(0)

# events url
NEXT_EVENTS_URL = None
def get_events(seq):
	global NEXT_EVENTS_URL
	if NEXT_EVENTS_URL is None:
		NEXT_EVENTS_URL = application_base + apps['_links']['events']['href']
 	print "--{0}. GET: {1}".format(seq, NEXT_EVENTS_URL)
 	events_response = requests.get(NEXT_EVENTS_URL,headers=headers)
 	print "--Response Code: {0}".format(events_response.status_code)
 	if 'resync' in events_response.json()['_links']:
 		NEXT_EVENTS_URL = application_base + events_response.json()['_links']['resync']['href']
 	else:
 		NEXT_EVENTS_URL = application_base + events_response.json()['_links']['next']['href']
 	return events_response

# parse events for messagingInvitation event
def parse_messagingInvitation_event(response_data):
	for sender_data in response_data['sender']:
		# sender rel can be commmunication (messageInvitation) or communication
 		if sender_data['rel'] in ['communication', 'conversation']:
 			for event_data in sender_data['events']:
 				if event_data['type'] not in ['deleted', 'added']:
	 				for event_type, event_value in event_data['_embedded'].items():
	 					if event_type in ['messagingInvitation', 'message']:
	 						return event_value
	return {}

# Receive messages
def receive_message():
	# invoke a plain GET to the myContacts url we found above. 
	
	r7_url = application_base + apps['_embedded']['people']['_links']['myContacts']['href']
	print "--7. GET: {0}".format(r7_url)
	r7 = requests.get(r7_url,headers=auth_headers)
	print "--Response Code: {0}".format(r7.status_code)
	for contact in r7.json()['_embedded']['contact']:
	    print "Name " + contact['name']

	while True:
	 	r8 = get_events(8)
	 	event_value = parse_messagingInvitation_event(r8.json())
	 	if event_value and event_value['direction'] == 'Incoming':
	 		if 'accept' in event_value['_links']:
		 		r16_url = application_base + event_value['_links']['accept']['href']
		 		print "--16. POST: {0}".format(r16_url)
		 		r16 = requests.post(r16_url,headers=headers)
		 		print "--Response Code: {0}".format(r16.status_code)
		 	else:
		 		if 'message' in event_value['_links']:
		 			raw_message = event_value['_links']['message']['href']
		 		elif 'plainMessage' in event_value['_links']:
		 			raw_message = event_value['_links']['plainMessage']['href']
		 		else:
		 			continue
		 		content_type, charset_data = raw_message.split(';')
		 		charset, data = charset_data.split(',')
			 	print '-----------------------------------------'
			 	print 'RECEIVED : %s' % data
			 	print '-----------------------------------------'


# send message
def send_message():
	r9_url = application_base + apps['_embedded']['communication']['_links']['startMessaging']['href']
	print "--9. POST: {0}".format(r9_url)
	r9 = requests.post(r9_url,headers=headers, data=json.dumps({
		"importance":"Normal",
	    "sessionContext":"33dc0ef6-0570-4467-bb7e-49fcbea8e944",
	    "subject":"Task Sample",
	    "telemetryId":None,
	    "to":"sip:somerandom@gmail.com",
	    "operationId":"5028e824-2268-4b14-9e59-1abad65ff393"
		}))
	print "--Response Code: {0}".format(r9.status_code)

	r10 = get_events(10)

	conversation_url = None
	event_value = parse_messagingInvitation_event(r10.json())
	if event_value:
		conversation_url = event_value['_links']['conversation']['href']

	if conversation_url:
		r12_url = application_base + conversation_url
		print "--12. GET: {0}".format(r12_url)
		r12 = requests.get(r12_url,headers=headers)
		print "--Response Code: {0}".format(r12.status_code)

		r13_url = application_base + r12.json()['_links']['messaging']['href'] + '/messages'
		print "--13. GET: {0}".format(r13_url)
		send_headers = copy.copy(headers)
		headers['Content-Type'] = 'text/plain'
		r13 = requests.post(r13_url,headers=headers, data="Whats up")
		print "--Response Code: {0}".format(r13.status_code)

		r14 = get_events(14)

		# terminate the conversation
		r15_url = application_base + event_value['_links']['messaging']['href'] + '/terminate'
		print "--15. POST: {0}".format(r15_url)
		r15 = requests.post(r15_url,headers=headers)
		print "--Response Code: {0}".format(r15.status_code)


send_message()
receive_message()