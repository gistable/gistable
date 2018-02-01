#!/usr/bin/env python
"""
james.py - Chief CLI.

USAGE: james.py ENV REF
  ENV - Environment defined in the config file to deploy to.
  REF - A git reference (like a SHA) to deploy.

Config: james.ini in the current directory should be an ini file with
one section per environment. Each environment should have a
`revision_url`, `chief_url`, and `password`. A special section,
`general`, may exist, which will can have one key: `username`. If no
username is given in general, the result of the command "whoami" will be
used.

Example Config:

    [general]
    username = bob

    [prod]
    revision_url = http://example.com/media/revision.txt
    chief_url = http://chief.example.com/example.prod
    password = lolpassword

    [stage]
    revision_url = http://stage.example.com/media/revision.txt
    chief_url = http://chief.example.com/example.stage
    password = omgsecret

Then you can use james.py like this:

    ./james.py stage fa0594dc16df3be505592b6346412c0a03cfe5bf

Answer the questions, and wait a bit, and a deploy will happen! You will
see the same output that you would if you deployed using the website.

Dependencies: requests
"""


import os
import subprocess
import sys
from ConfigParser import ConfigParser, NoOptionError, NoSectionError

import requests


def git(*args, **kwargs):
    args = ['git'] + list(args)
    if kwargs.pop('out', None) == 'print':
        subprocess.check_call(args, **kwargs)
        return None
    else:
        return subprocess.check_output(args, **kwargs)


def config(environment, key, die=False, memo={}):
    if 'config' not in memo:
        memo['config'] = ConfigParser()
        memo['config'].read('james.ini')

    try:
        return memo['config'].get(environment, key)
    except NoSectionError if die else None:
        print 'No such environment %s' % environment
        sys.exit(2)
    except NoOptionError if die else None:
        print 'Missing key %s in environment %s' % (key, environment)
        sys.exit(4)


def usage():
    print 'USAGE: %s ENV REF' % os.path.split(sys.argv[0])[-1]
    print '  ENV - Environment defined in the config file to deploy to.'
    print '  REF - A git reference (like a SHA) to deplot'


def check_args():
    if len(sys.argv) != 3:
        usage()
        sys.exit(1)

    environment = sys.argv[1]
    local_commit = sys.argv[2]

    return environment, local_commit


def check_ancestry(older, newer):
    commits = git('rev-list', newer).split('\n')
    return older in commits


def yes_no(prompt):
    sys.stdout.write(prompt + ' ')
    ret = raw_input('[y/n] ')
    while ret not in ['y', 'n']:
        ret = raw_input('Please choose "y" or "n" [y/n] ')
    return ret == 'y'


def username():
    try:
        return config('general', 'username').strip()
    except (NoSectionError, NoOptionError):
        return subprocess.check_output(['whoami']).strip()


def webhooks(env, log_spec):
    if config(env, 'newrelic'):
        print 'Running New Relic deploy hook...',
        changelog = git('log', '--pretty=oneline', log_spec)
        rev = changelog.split('\n')[0].split(' ')[0]
        data = {
            'app_name': config('newrelic', 'app_name', die=True),
            'application_id': config('newrelic', 'application_id', die=True),
            'description': 'Test chief deploy via james.py',
            'revision': rev,
            'changelog': changelog,
            'user': username(),
        }
        url = 'https://rpm.newrelic.com/deployments.xml'
        data = dict(('deployment[%s]' % k, v) for k, v in data.items())
        headers = { 'x-api-key':  config('newrelic', 'api_key') }

        res = requests.post(url, data=data, headers=headers)
        print res.status_code, res.text

        print 'done'

def main():
    environment, commit = check_args()

    revision_url = config(environment, 'revision_url', die=True)
    chief_url = config(environment, 'chief_url', die=True)
    password = config(environment, 'password', die=True)

    if not revision_url.startswith('http'):
        revision_url = 'http://' + revision_url
    if not chief_url.startswith('http'):
        chief_url = 'http://' + chief_url

    environment_commit = requests.get(revision_url).text.strip()
    local_commit = git('rev-parse', commit).strip()

    print 'Environment: {0}'.format(environment)
    print 'Pushing as : {0}'.format(username())
    print 'Pushing    : {0} ({1})'.format(commit, local_commit[:8])
    print 'On server  : {0}'.format(environment_commit[:8])

    log_spec = environment_commit + '..' + local_commit

    if environment_commit.startswith(local_commit):
        print 'Pushing out (again):'
        git('log', '--oneline', '-n', '1', local_commit, out='print')

    elif not check_ancestry(environment_commit, local_commit):
        print 'Pushing from different branch:'
        git('log', '--oneline', '-n', '1', local_commit, out='print')

    else:
        print 'Pushing out:'
        git('log', '--oneline', log_spec, out='print')

    print ''

    if yes_no('Proceed?'):
        payload = {
            'who': username(),
            'password': password,
            'ref': local_commit,
        }
        res = requests.post(chief_url, data=payload, stream=True)
        for chunk in res.iter_content():
            sys.stdout.write(chunk)
            sys.stdout.flush()

        # Chief doesn't finish with a newline. Rude.
        print ''

        webhooks(environment, log_spec)

    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
