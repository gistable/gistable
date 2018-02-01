# encoding: utf-8

from __future__ import print_function
from json import dumps as to_json
from datetime import datetime, timedelta
import requests

URL_BASE="https://i.doit.im/tasks/%s"
DOIT_BOXES = ('inbox', 'today', 'next', 'tomorrow', 'scheduled', 'someday', 'waiting')
COOKIES = { 'autologin': 'Your Autologin Cookie Here' }

PROJECT_TRANS = { 'Project Name With Space': 'ProjectNameWithoutSpace' }
TAG_TRANS = { 'TagBefore': 'TagAfter' }
PRIORITY_TRANS = ('', 'L', 'M', 'H')
TIME_OFFSET = timedelta(hours=8)

def fetch_doit_items(): return sum(map(fetch_doit_box, DOIT_BOXES), [])
def fetch_doit_box(path): return requests.get(URL_BASE % path, cookies=COOKIES).json['entities']

def doit2task(item):
    created_at = trans_time(item['created'])

    task = {
        'description': item['title'],
        'status': 'pending',
        'uuid': item['uuid'],
        'entry': created_at
    }

    if item['start_at'] > 0:
        task['due'] = trans_time(item['start_at'])

    if item['priority'] > 0:
        task['priority'] = PRIORITY_TRANS[item['priority']]

    if item['project_name']:
        task['project'] = trans_project_name(item['project_name'])

    if item['tags']:
        task['tags'] = trans_tags(item['tags'])

    if item['notes']:
        task['annotations'] = [{ 'entry': created_at, 'description': item['notes'] }]

    return task

def trans_project_name(name): return PROJECT_TRANS.get(name, None) or name
def trans_tags(tags): return map(lambda tag: TAG_TRANS.get(tag, None) or tag, tags)

def trans_time(value):
    time = datetime.fromtimestamp(value / 1000) - TIME_OFFSET
    return '%sZ' % time.isoformat().replace('-', '').replace(':', '')

if __name__ == '__main__':
    items = fetch_doit_items()

    for item in items:
        task = doit2task(item)
        print(to_json(task, ensure_ascii=False).encode('utf-8'), '\n')