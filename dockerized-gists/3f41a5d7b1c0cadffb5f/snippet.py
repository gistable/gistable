import logging

import requests

logging.captureWarnings(True)

SERVER = 'my-jenkins'
JOB_FILTER = 'test'
API_TOKEN = '<my-jenkins-api-token>'
USER = 'glombard'


def get_jobs():
  url = 'https://%s/api/json?pretty=true' % SERVER
  response = requests.get(url)
  data = response.json()
  return data['jobs']


def backup_job(name, url):
  url = url + 'config.xml'
  response = requests.get(url, auth=(USER, API_TOKEN), stream=True)
  if not response.ok:
    print 'error %d getting job config: %s' % (response.status_code, url)
  else:
    print name
    with open(name + '.xml', 'w') as output:
      for block in response.iter_content(2048):
        output.write(block)


jobs = get_jobs()
for j in jobs:
  if j['name'].startswith(JOB_FILTER):
    backup_job(j['name'], j['url'])
