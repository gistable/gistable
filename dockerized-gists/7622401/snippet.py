import requests
import operator

companies = ["facebook", "aws", "google", "yahoo", "dropbox", "twitter", "paypal", "linkedin", "mozilla", "adobe"]
api_url = "https://api.github.com/orgs/{}/repos"
data = {}

for company in companies:
	data[company] = {'forks': 0, 'stars': 0, 'repos': 0, 'languages': {}}
	r = requests.get(api_url.format(company))
	json = r.json()
	while "next" in r.links:
		r = requests.get(r.links['next']['url'])
		json += r.json()
	for repo in json:
		try:
			data[company]['repos'] += 1
			data[company]['forks'] += repo['forks_count']
			data[company]['stars'] += repo['watchers_count']
			data[company]['languages'][repo['language']] = data[company]['languages'].get(repo['language'], 0) + repo['size']
		except:
			continue
			
print "COMPANY", "REPOS", "FORKS", "STARS"
for company in data:
	print company, data[company]['repos'], data[company]['forks'], data[company]['stars'], max(data[company]['languages'].iteritems(), key=operator.itemgetter(1))[0]