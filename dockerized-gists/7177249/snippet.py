# pip install requests
import requests
import json
 
url_template = 'https://api.foursquare.com/v2/users/self/checkins?limit=250&oauth_token={}&v=20131026&offset={}'
 
# If you navigate to https://developer.foursquare.com/docs/explore, Foursquare
# will generate an OAuth token for you automatically. Cut and paste that token
# below.
token = ""
offset = 0
data = []
 
with open("/tmp/checkins.json", 'w') as f:
    while True:
        response = requests.get(url_template.format(oauth_token, offset))
        if len(response.json()['response']['checkins']['items']) == 0:
            break

        data.append(response.json())
        offset += 250
            
    f.write(json.dumps(data))