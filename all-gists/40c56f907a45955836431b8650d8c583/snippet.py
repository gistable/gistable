import requests
def test_url(url):
	test = requests.get(url)
	return test