import requests
import json

api_key = 'your_api_key'
url = "https://api.fullcontact.com/v2/person.json"

def whois(**kwargs):
  if 'apiKey' not in kwargs:
    kwargs['apiKey'] = api_key
  r = requests.get(url, params=kwargs)
  return json.loads(r.text)