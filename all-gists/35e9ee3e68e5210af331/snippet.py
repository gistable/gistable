'''
HTTP Reuests has following parameters: 
1)Request URL 
2)Header Fields
3)Parameter 
4)Request body
'''
#!/usr/bin/env python

import requests
import json

GITHUB_API="https://api.github.com"
API_TOKEN='your_token_goes_here'

#form a request URL
url=GITHUB_API+"/gists"
print "Request URL: %s"%url

#print headers,parameters,payload
headers={'Authorization':'token %s'%API_TOKEN}
params={'scope':'gist'}
payload={"description":"GIST created by python code","public":True,"files":{"python request module":{"content":"Python requests has 3 parameters: 1)Request URL\n 2)Header Fields\n 3)Parameter \n4)Request body"}}}

#make a requests
res=requests.post(url,headers=headers,params=params,data=json.dumps(payload))

#print response --> JSON
print res.status_code
print res.url
print res.text
j=json.loads(res.text)

# Print created GIST's details
for gist in range(len(j)):
 print "Gist URL : %s"%(j['url'])
 print "GIST ID: %s"%(j['id'])

