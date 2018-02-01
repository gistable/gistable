import requests  # pip install requests
import json
import base64
import hashlib
import time #for nonce

api_key = ''
api_secret = ''

#url = 'https://bitfinex.com/api/v1/order/new'
url = 'https://bitfinex.com/api/v1/balances'

payloadObject = {
           'request':'/api/v1/balances',
           'nonce':time.time(),
           'options':{}
           }

#payload = {
#            'request':'/v1/'
#            }

# payload buyorder, btcusd 100 @ $1.00
# payload = { 
#            'request':'/v1/order/new',
#            'nonce':time.time(),
#            'options' : {'symbol':'btcusd',
#             'amount':'100.00000000',
#             'price':'1.00',
#             'exchange':'bitfinex',
#             'side':'buy',
#             'type':'limit'}
#            }

payload_json = json.dumps(payloadObject)
print payload_json

payload = str(base64.b64encode(payload_json))
print payload

m = hashlib.sha384(api_secret).update(payload).hexdigest()

# headers
headers = {
           'X-BFX-APIKEY' : api_key,
           'X-BFX-PAYLOAD' : base64.b64encode(payload_json),
           'X-BFX-SIGNATURE' : m
           }

r = requests.get(url, data={}, headers=headers)

print 'Response Code: ' + str(r.status_code) 
print 'Response Header: ' + str(r.headers)
print 'Response Content: '+ str(r.content)