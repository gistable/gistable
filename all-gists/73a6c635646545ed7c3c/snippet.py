import requests
import re
import sys

tags = ['', 'python', 'javascript', 'django', 'web', 'google', 'java', 'ajax',
        'rails', 'plugin', 'android', 'cplusplus', 'mysql', 'dotnet', 'game',
        'appengine', 'php', 'flash', 'jquery', 'database', 'gwt']

seen_tags = set(tags)

projects = set()

def get_tag():
    i = 0
    while i < len(tags):
        yield tags[i]
        i += 1

def add_tag(tag):
    if tag not in seen_tags:
        tags.append(tag)
        seen_tags.add(tag)

SEARCH_URL = 'https://code.google.com/hosting/search?q=label%3A'


for tag in get_tag():
    r = requests.get(SEARCH_URL+tag)

    if '&' not in tag:
        try:
            num_result = int(re.search('Results \d+ - \d+ of (\d+)', r.text).group(1))
        except:
            print(':( could not get {}'.format(SEARCH_URL+tag), file=sys.stderr)
            continue
        for i in range(50, num_result, 10):
            add_tag(tag+'&start='+str(i))
        continue

    new_tags = set(map(str.lower, re.findall('<a href="/hosting/search\?q=label:([^"]+)">', r.text)))
    for tag in new_tags:
        add_tag(tag)

    new_projects = set(re.findall('<a href="/p/([^/"]+)/">', r.text)) - projects

    if new_projects:
        print('https://code.google.com/export-to-github/export?project='+'\nhttps://code.google.com/export-to-github/export?project='.join(new_projects))

    projects |= new_projects
