#!/usr/bin/python

import collections
import json
import os
import signal
import sys
import subprocess
# require pygithub installed
from github import Github

github_token = os.environ.get('GITHUB_TOKEN') or sys.exit('GITHUB_TOKEN is not defined')
github_user = 'MY_USER'
github_repository = 'MY_REPOSITORY'

# Use project.query method to find out projects PHIDs
# e.g. https://secure.phabricator.com/conduit/method/project.query/
default_project = 'PHID-PROJ-xxxxxxxxxxxxxxxxxxxx'
project = {
    'My project': 'PHID-PROJ-xxxxxxxxxxxxxxxxxxxx',
}


def cmd_runner(task, method="createtask"):
    try:
        arguments = ['arc', 'call-conduit', 'maniphest.%s' % method]
        proc = subprocess.Popen(arguments,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                universal_newlines=False,
                                preexec_fn=lambda:
                                signal.signal(signal.SIGPIPE, signal.SIG_DFL))
    except (OSError, ValueError) as e:
        raise ValueError("%s" % e)

    data = proc.communicate(input=task)[0]
    if proc.returncode != 0:
        raise ValueError("command has failed with code '%s'" % proc.returncode)

    return data


def main():
    github = Github(github_token)
    user = github.get_user(github_user)
    repo = user.get_repo(github_repository)
    issues = repo.get_issues().reversed
    for issue in issues:
        projects = []
        labels = issue.labels
        for label in labels:
            projects.append(project.get(label.name, default_project))

        task = json.dumps({'title': issue.title,
                           'description': 'Imported from: %s\n---\n%s' % (issue.html_url,
                                                                          issue.body),
                           'projectPHIDs': projects},
                          indent=2, separators=(',', ': '))
        print '%s\n' % task
        response = cmd_runner(task)
        data = json.loads(response, object_pairs_hook=collections.OrderedDict)
        task_id = data['response']['id']

        comments = issue.get_comments()
        for comment in comments:
            task = json.dumps({'id': task_id,
                               'comments': '%s commented on %s:\n---\n%s' % (comment.user.name,
                                                                             comment.created_at.strftime("%B %-d"),
                                                                             comment.body)},
                              indent=2, separators=(',', ': '))
            print '%s\n' % task
            cmd_runner(task, 'update')


if __name__ == '__main__':
    main()
