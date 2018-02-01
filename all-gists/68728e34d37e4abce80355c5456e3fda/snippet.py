#   1. Install the requests module for python.
#       pip install requests
#   2. Add script arguments in PlexPy.
#       {user} {user_id} {ip_address}

import requests
import sys

user = sys.argv[1]
user_id = sys.argv[2]
ip_address = sys.argv[3]

SUBJECT_TEXT = "PlexPy Notification"
BODY_TEXT = "User <b>%s</b> has used a new IP address: %s" % (user, ip_address)

## EDIT THESE SETTINGS ##
PLEXPY_APIKEY = 'XXXXXX'  # Your PlexPy API key
PLEXPY_URL = 'http://localhost:8181/'  # Your PlexPy URL
AGENT_ID = 10  # The notification agent ID for PlexPy

def get_user_ip_addresses(user_id='', ip_address=''):
    # Get the user IP list from PlexPy
    payload = {'apikey': PLEXPY_APIKEY,
               'cmd': 'get_user_ips',
               'user_id': user_id,
               'search': ip_address}
               
    try:
        r = requests.get(PLEXPY_URL.rstrip('/') + '/api/v2', params=payload)
        response = r.json()

        if response['response']['result'] == 'success':
            data = response['response']['data']
            if data.get('error'):
                raise Exception(data['error'])
            else:
                sys.stdout.write("Successfully retrieved UserIPs data.")
                if response['response']['data']['recordsFiltered'] == 0:
                    sys.stdout.write("IP has no history.")
                else:
                    sys.stdout.write("IP has history, killing script.")
                    exit()
        else:
            raise Exception(response['response']['message'])
    except Exception as e:
        sys.stderr.write("PlexPy API 'get_user_ip_addresses' request failed: {0}.".format(e))

def send_notification(arguments=None, ip_address=None, user_id=None):
    # Format notification text
    try:
        subject = SUBJECT_TEXT
        body = BODY_TEXT
    except LookupError as e:
        sys.stderr.write("Unable to substitute '{0}' in the notification subject or body".format(e))
        return None
    # Send the notification through PlexPy
    payload = {'apikey': PLEXPY_APIKEY,
               'cmd': 'notify',
               'agent_id': AGENT_ID,
               'subject': subject,
               'body': body}

    try:
        r = requests.post(PLEXPY_URL.rstrip('/') + '/api/v2', params=payload)
        response = r.json()
        
        if response['response']['result'] == 'success':
            sys.stdout.write("Successfully sent PlexPy notification.")
        else:
            raise Exception(response['response']['message'])
    except Exception as e:
        sys.stderr.write("PlexPy API 'notify' request failed: {0}.".format(e))
        return None


get_user_ip_addresses(user_id=user_id, ip_address=ip_address)
send_notification(user_id=user_id, ip_address=ip_address)