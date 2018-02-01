import requests
import time
import json

token = ''

#Delete files older than this:
ts_to = int(time.time()) - 30 * 24 * 60 * 60

def list_files():
  params = {
    'token': token
    ,'ts_to': ts_to
    ,'count': 1000
  }
  uri = 'https://slack.com/api/files.list'
  response = requests.get(uri, params=params)
  return json.loads(response.text)['files']

def delete_files(file_ids):
  count = 0
  num_files = len(file_ids)
  for file_id in file_ids:
    count = count + 1
    params = {
      'token': token
      ,'file': file_id
      }
    uri = 'https://slack.com/api/files.delete'
    response = requests.get(uri, params=params)
    print count, "of", num_files, "-", file_id, json.loads(response.text)['ok']

files = list_files()
file_ids = [f['id'] for f in files]
delete_files(file_ids)