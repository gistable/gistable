'''
Steps:
  1. Create any milestones
  2. Create any labels
  3. Create each issue, linking them to milestones and labels
  3.1: Update status for new issue if closed
  4: Create all the comments for each issue
'''
import getpass
import json
import random
import human_curl as hurl
#hurl.Request.SUPPORTED_METHODS += ('PATCH',)
#didn't work, just use POST

import re
from htmlentitydefs import name2codepoint
def htmlentitydecode(s):
  if s is None: return ''
  s = s.replace(' '*8, '')
  return re.sub('&(%s);' % '|'.join(name2codepoint), 
      lambda m: unichr(name2codepoint[m.group(1)]), s)

from lxml import objectify
from collections import defaultdict

all_text = open(raw_input('Path to xml file: ')).read()
all_xml = objectify.fromstring(all_text)

projects = {}
addtag = raw_input('Make tag for project and add to all[y/n]: ').lower()
addtag = (addtag == 'y')

def add(item):
  try:
    proj = item.project.get('key')
  except AttributeError:
    proj = item.key.text.split('-')[0]

  if proj not in projects:
    projects[proj] = {'Milestones': defaultdict(int), 'Components': defaultdict(int), 'Labels': defaultdict(int), 'Issues': []}

  try:
    resolved_at = ', resolved="' + item.resolved.text + '"'
  except AttributeError:
    resolved_at = ''

  projects[proj]['Issues'].append({"title": item.title.text,
    "body": '<b><i>[reporter="' + item.reporter.get('username') + '", created="' + item.created.text + '"' + resolved_at + ']</i></b>\n' + htmlentitydecode(item.description.text),
    "labels": [],
    'open': str(item.status.get('id')) not in ('5','6'),
    'comments': []
    })

  # github doesn't want you to assign to any name,
  # must be a github user
  #if item.assignee.get('username') != '-1':
  #  projects[proj]['Issues'][-1]['assignee'] = item.assignee.get('username')

  try:
    projects[proj]['Milestones'][item.fixVersion.text] += 1
    # this prop will be deleted later:
    projects[proj]['Issues'][-1]['milestone_name'] = item.fixVersion.text 
  except AttributeError:
    pass
  try:
    projects[proj]['Components'][item.component.text] += 1
    projects[proj]['Issues'][-1]['labels'].append(item.component.text)
  except AttributeError:
    pass
  try:
    for label in item.labels.label:
      projects[proj]['Labels'][label.text] += 1
      projects[proj]['Issues'][-1]['labels'].append(label.text)
  except AttributeError:
    pass
  try:
    for comment in item.comments.comment:
      projects[proj]['Issues'][-1]['comments'].append('<b><i>[author="' +
          comment.get('author') + '", created="' +
          comment.get('created') + '"]</i></b>\n' +
          htmlentitydecode(comment.text))
  except AttributeError:
    pass

for item in all_xml.channel.item:
  add(item)

def prettify(projects):
  def hist(h):
    for key in h.iterkeys():
      print ('%30s(%5d): ' + h[key]*'#') % (key, h[key])
    print

  for proj in projects.iterkeys():
    print proj + ':\n  Milestones:'
    hist(projects[proj]['Milestones'])
    print '  Components:'
    hist(projects[proj]['Components'])
    print '  Labels:'
    hist(projects[proj]['Labels'])
    print

prettify(projects)
print
print 'Components will be combined with labels as github labels...'

proj = raw_input('Project to use: ')
us = raw_input('Repo User: ')
repo = raw_input('Repo to use: ')
user = raw_input('User: ')
pw = getpass.getpass('Pass: ')
url_frag = 'https://api.github.com/repos/' + us + '/' + repo
print 'Making milestones...', url_frag + '/milestones'
print

for mkey in projects[proj]['Milestones'].iterkeys():
  data = {'title': mkey}
  r = hurl.post(url_frag + '/milestones',
      json.dumps(data),
      auth=(user, pw))
  # overwrite histogram data with the actual milestone id now
  if r.status_code == 201:
    content = json.loads(r.content)
    projects[proj]['Milestones'][mkey] = content['number']
    print mkey
  else:
    if r.status_code == 422: # already exists
      ms = json.loads(hurl.get(url_frag + '/milestones?state=open').content)
      ms += json.loads(hurl.get(url_frag + '/milestones?state=closed').content)
      f = False
      for m in ms:
        if m['title'] == mkey:
          projects[proj]['Milestones'][mkey] = m['number']
          print mkey, 'found'
          f = True
          break
      if not f:
        exit('Could not find milestone: ' + mkey)
    else:
      print 'Failure!', r.status_code, r.content

print
print 'Making labels...'
projects[proj]['Components'].update(projects[proj]['Labels'])
if proj == 'DDB':
  projects[proj]['Components']['DDB'] = 0
if addtag:
  projects[proj]['Components'][proj] = 0
for lkey in projects[proj]['Components'].iterkeys():
  data = {'name': lkey, 'color': '%.6x' % random.randint(0, 0xffffff)}
  r = hurl.post(url_frag + '/labels',
      json.dumps(data),
      auth=(user, pw))
  if r.status_code == 201:
    print lkey
  else:
    print 'Failure!', r.status_code, r.content

print
print 'Creating each issue...'
for issue in projects[proj]['Issues']:
  if 'milestone_name' in issue:
    issue['milestone'] = projects[proj]['Milestones'][ issue['milestone_name'] ]
    del issue['milestone_name']
  op = issue['open']
  del issue['open']
  comments = issue['comments']
  del issue['comments']
  if 'Connectors' in issue['labels'] and 'connectors' not in issue['labels']:
    issue['labels'].append('connectors')
  if proj == 'DDB':
    issue['labels'].append('DDB')
  if addtag:
    issue['labels'].append(proj)

  #screwups:
  #t = issue['title']
  #if proj == 'FNL' and int(re.search('\[[A-Z]+-([0-9]+)\]', t).groups()[0]) >= 56:
  #  print 'skipping ' + t
  #  continue
  #if proj == 'FRG' and int(re.search('\[[A-Z]+-([0-9]+)\]', t).groups()[0]) >= 365:
  #  print 'skipping ' + t
  #  continue
  #if raw_input('skip ' + issue['title'] + '? ').lower() == 'y':
  #  continue
  #if max(t.find('FRG-415'), t.find('FRG-417'), t.find('FRG-418'), t.find('FRG-419'), t.find('FRG-421'), t.find('FRG-423'), t.find('FRG-424'), t.find('FRG-425'), t.find('FRG-427'), t.find('FRG-428'), t.find('FRG-429')) > -1:
  #  print 'skipping ' + t
  #  continue


  r = hurl.post(url_frag + '/issues', json.dumps(issue), auth=(user,pw),
      headers={'Accept': 'application/vnd.github.beta.html+json'})

  if r.status_code == 201:
    content = json.loads(r.content)
    print 'Created issue:', issue['title']
    if op == False:
      # this is supposed to be hurl.method.patch() but it fails
      r2 = hurl.post(url_frag + '/issues/' + str(content['number']),
          json.dumps({'state': 'closed'}), auth=(user,pw))
      if r2.status_code == 200:
        print 'Closed issue'
      else:
        print 'Failed to close issue!', r2.status_code, r2.content

    for comment in comments:
      r3 = hurl.post(url_frag + '/issues/' + str(content['number']) + '/comments',
          json.dumps({'body': comment}), auth=(user,pw),
          headers={'Accept': 'application/vnd.github.beta.html+json'})
      if r3.status_code == 201:
        print 'Added comment',
      else:
        print 'Failed to add comment!', r3.status_code, r3.content

    print
  else:
    print "FFFFFFFFFFFFFFFuuuuuuuuuuuu, couldn't make issue:", issue
    print '*'*10
    print r.status_code, r.content
  print

