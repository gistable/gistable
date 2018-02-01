#!/usr/bin/env python
from github import Github
import urllib2
import codecs
import sys 
import re
UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)

oauthToken = open('.oauthToken', 'r').read()
github = Github(login_or_token=oauthToken)

def print_repo(repo_url):
	match = re.match('.+github.com/([^/]+/[^/]+).*', repo_url)
	if match is not None:
		repo_name = match.group(1)
		repo = github.get_repo(repo_name)
		for item in [
			repo.owner.name,
			repo.owner.login,
			repo.name,
			repo.created_at,
			repo.description,
			repo.language,
			repo.stargazers_count]:
			print item if item else '',
			print '\t',
	print ''

url = 'https://docs.google.com/spreadsheets/d/1XvGfi3TxWm7kuQ0DUqYrO6cxva196UJDxKTxccFqb9U/pub?gid=0&single=true&output=tsv'
response = urllib2.urlopen(url)
tsv = response.read()
lines = tsv.split('\r\n')
keys = lines.pop(0).split('\t')
for line in lines:
	values = line.split('\t')
	item = dict(zip(keys, values))
	repo_url = item['GitHub']
	print_repo(repo_url)