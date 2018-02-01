import argparse
import string
import requests
import time

parser = argparse.ArgumentParser(
	description='Get all Google Suggest results for a query.')
parser.add_argument('query')
parser.add_argument('--sleep', type=float, default=0.1)
parser.add_argument('--verbose', action='store_true')
args = parser.parse_args()

results = set()
query = args.query.replace(' ', '+')
for character in string.lowercase:
	url = 'http://google.com/complete/search?client=chrome&q=' + query + '+' + character
	if args.verbose:
		print(url)
	cur = requests.get(url).json()
	suggestions = cur[1]
	if len(suggestions):
		suggesttypes = cur[4]['google:suggesttype']
		relevances = cur[4]['google:suggestrelevance']
		for suggestion, suggesttype, relevance in zip(suggestions, suggesttypes, relevances):
			if suggesttype == 'QUERY':
				results.add(suggestion)
			if args.verbose:
				print '\t'.join([str(relevance), suggesttype, suggestion])
		time.sleep(args.sleep)
results = list(results)
results.sort()
for result in results:
	print(result)
