#!/usr/bin/env python
'''
Harvest (www.getharvest.com) does not support setting monthly budgets for projects.
The recommended workaround is creating a new project every month. This script is
supposed to run on the first of every month and uses the Harvest API in order to
archive last month's projects and create new ones for the current month. Members
and tasks are automatically copied over to the new project.

Projects with monthly budgets need to fulfill two requirements:
    1. They need to have a budget set
    2. The name needs to end in "YYYY-MM", meaning year and month of the current 
       month. Example would be: "Website maintenance 2011-10".

An example crontab entry would be:

    0 1 1 * * USERNAME=info@jonasundderwolf.de PASSWORD=xyz /path/to/harvest_monthly_budgets.py

Uses the "requests" library (http://pypi.python.org/pypi/requests)
'''
import os
import re
import datetime
import json
import requests

AUTH = (os.environ['USERNAME'], os.environ['PASSWORD'])

today = datetime.date.today().replace(day=1)
month = today.strftime('%Y-%m')
# previous month
y, m = today.year, today.month
if m == 1: y -= 1; m = 12
else: m -= 1
today = today.replace(year=y, month=m)
prev_month = today.strftime('%Y-%m')

EXCLUDE_FIELDS = ('active_task_assignments_count', 'active_user_assignments_count', 'cache_version',
    'created_at', 'earliest_record_at', 'hint-earliest-record-at', 'hint-latest-record-at', 'id',
    'latest_record_at', 'name', 'updated_at')

kwargs = {
    'auth': AUTH,
    'headers': {
        'Accept': 'application/json',
        'Content-Type': 'application/json'},
}
base_url = 'https://jonasundderwolf.harvestapp.com/projects'
projects = json.load(requests.get(base_url, **kwargs))
for p in projects:
    project = p['project']
    if project['active'] and project['name'].endswith(prev_month) and (
            (project.get('budget') and float(project.get('budget'))) or
            (project.get('cost_budget') and float(project.get('cost_budget')))):
        print 'Copy project: %s' % project['name']
        pid = project['id']

        # create new project
        new_project = {
            'name': project['name'].replace(prev_month, month),
        }
        for field, value in project.items():
            if field not in EXCLUDE_FIELDS:
                new_project[field] = value

        print '> create new project: %s' % new_project['name']
        r = requests.post(base_url, data=json.dumps({'project': new_project}), **kwargs)
        if r.status_code != 201:
            print '>> Could not create new Project: %s' % r.read()
            continue
        # fetch new pid
        new_pid = re.findall('(\d+)$', r.headers['Location'])[0]

        # get user assignments
        r = requests.get('%s/%s/user_assignments' % (base_url, pid), **kwargs)
        users = json.loads(r.content)
        print '> Users:'
        for u in users:
            nu = {'user': {'id': u['user_assignment']['user_id']}}
            print '>> adding user: %s' % nu['user']['id']
            r = requests.post('%s/%s/user_assignments' % (base_url, new_pid), data=json.dumps(nu), **kwargs)
            if r.status_code != 201:
                print '>> Could not assign user %s to new Project' % u['user']['user_id']

        # get task assignments
        r = requests.get('%s/%s/task_assignments' % (base_url, pid), **kwargs)
        tasks = json.loads(r.content)
        print '> Tasks:'
        for t in tasks:
            nt = {'task': {'id': t['task_assignment']['task_id']}}
            print '>> adding task: %s' % nt['task']['id']
            r = requests.post('%s/%s/task_assignments' % (base_url, new_pid), data=json.dumps(nt), **kwargs)
            if r.status_code != 201:
                print '>> Could not assign user %s to new Project' % u['user']['user_id']

        # disable old project
        r = requests.put('%s/%s/toggle' % (base_url, pid), **kwargs)
        print '> diabling old project!'
        if r.status_code != 200:
           print '>> Could not toggle old project'
