import json
import os

import requests


GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
if GITHUB_TOKEN is None:
    raise Exception('Missing GITHUB_TOKEN from os.environ')

DEFAULT_PHAB_PROJ = 'PHID-PROJ-tsbdozvucsrp4hsooqg'

GITHUB_LABEL_TO_PHAB_PROJ_MAP = {
    'ios sdk': 'PHID-PROJ-tbul5vwnukmnurumxaz',
    'android sdk': 'PHID-PROJ-ozxqke5y5gcufknuc',
    'applescript': 'PHID-PROJ-ll3t6p5grwiurc54v2c',
    'docs': 'PHID-PROJ-ft4fmhvevxppqdege',
}

def get_issue(owner, repo, issue_number):
    auth = (GITHUB_TOKEN, 'x-oauth-basic')

    headers = {
        'User-Agent': 'GitHub-Issue-To-Phab-Task'
    }

    url = 'https://api.github.com/repos/%s/%s/issues/%s' % (
        owner,
        repo,
        issue_number
    )
    r = requests.get(
        url=url,
        headers=headers,
        auth=auth,
    )

    r.raise_for_status()

    return r.json()


def github_issue_to_phab_json(github_issue):
    task_description = "Original report: %s\n\n---\n%s\n" % (
        github_issue['html_url'],
        github_issue['body']
    )

    phab_projects = [
        DEFAULT_PHAB_PROJ,
    ]

    for label in github_issue['labels']:
        phab_project = GITHUB_LABEL_TO_PHAB_PROJ_MAP.get(label['name'])
        if phab_project is not None:
            phab_projects.append(phab_project)

    phab_task = {
        'title': github_issue['title'],
        'description': task_description,
        'projectPHIDs': phab_projects
    }

    return json.dumps(phab_task, indent=2, sort_keys=True)


def main():
    """
    Example usage::

        $ python github-issue-to-phab-task.py | arc call-conduit maniphest.createtask
    """
    owner = 'rdio'
    repo = 'api'
    issue_number = 118

    github_issue = get_issue(owner, repo, issue_number)
    print github_issue_to_phab_json(github_issue)


if __name__ == '__main__':
    main()
