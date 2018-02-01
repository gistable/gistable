#!/usr/bin/env python

import os
import sys
import urllib2
import json

'''
This script queries Github for source and target branches of a pull request
and updates environment variables at TeamCity CI to make these variable
available in the builds.

Usage: python teamcity_github_pr_branch.py <pull_request_id>

Before using the script from your TeamCity installation, do the following.

1. Update the constants defined below.
2. Export environment variable TEAMCITY_GITHUB_ACCESS_TOKEN containing your personal access token to Github.
3. In TeamCity project configuration, add the following empty parameters:
    env.GITHUB_PULL_REQUEST_BASE_REF
    env.GITHUB_PULL_REQUEST_HEAD_REF
After you run the script from one of your build steps, these variables will be
resolved and you'll be able to use them as environment variables in next build steps.
'''

GITHUB_REPO_OWNER = 'Terminator'
GITHUB_REPO_NAME = 'Skynet'


GITHUB_API_URL = 'https://api.github.com/repos/%(owner)s/%(repo)s/pulls/%(number)s'


def create_request():
    if len(sys.argv) == 1:
        raise Exception('Pull request id is not set, you should submit it as the first command-line argument')
    pr_id = sys.argv[1]
    access_token = os.environ.get('TEAMCITY_GITHUB_ACCESS_TOKEN', '-1')
    if access_token == '-1':
        raise Exception('Access token is empty, ensure that TEAMCITY_GITHUB_ACCESS_TOKEN env var is set')
    url = GITHUB_API_URL % {'owner': GITHUB_REPO_OWNER, 'repo': GITHUB_REPO_NAME, 'number': pr_id}
    request = urllib2.Request(url)
    request.add_header('Accept', 'application/vnd.github.v3+json')
    request.add_header('Authorization', 'token %s' % access_token)
    return request


def export_refs(json_data):
    base_ref = json_data['base']['ref']
    head_ref = json_data['head']['ref']
    print '##teamcity[setParameter name=\'env.GITHUB_PULL_REQUEST_BASE_REF\' value=\'%s\']' % base_ref
    print '##teamcity[setParameter name=\'env.GITHUB_PULL_REQUEST_HEAD_REF\' value=\'%s\']' % head_ref


def do_the_job():
    request = create_request()
    response = urllib2.urlopen(request)
    status = response.getcode()

    if status == 200:
        data = json.load(response)
        export_refs(data)
    else:
        raise Exception('Unexpected error code %d when fetching pull request details' % status)


if __name__ == "__main__":
    try:
        do_the_job()
    except Exception, e:
        print 'exception: %s' % e.args[0]
        exit(1)
