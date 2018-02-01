import urllib.request
import json
from pprint import pprint

url = 'https://graph.facebook.com/fmasanori'
resp = urllib.request.urlopen(url).read()
data = json.loads(resp.decode('utf-8'))
pprint (data)


