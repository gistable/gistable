import requests
import pandas as pd
s = requests.Session()
s.headers.update({'Content-Type': 'application/json'})
s.auth = ('USERNAME/token','TOKEN')
df = pd.read_csv('./support_addy.csv')

for count, row in df.iterrows():
	name = row[0]
	address = row[1]
	payload = '{"recipient_address": {"name":"' + str(name)+'", "email": "'+str(address)+'", "default": false }}'
	r = s.post("https://SUBDOMAIN.zendesk.com/api/v2/recipient_addresses.json", data=payload)
	print "Request completed with response " + str(r.status_code)