import requests

def checkName(name):
	values = { "new_username" : name }
	r = requests.post("https://login.skype.com/json/validator", values)
	return "not available" in r.json()[u'data'][u'markup']
