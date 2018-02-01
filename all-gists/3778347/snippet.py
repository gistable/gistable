#!/usr/bin/env python

"""
This script helps migrating issues from Bitbucket to GitHub.

It currently ignores milestones completly and doesn't care whether an issue is
open, new or on hold. As long as it's not closed it's considered open.

To use it, install python-bitbucket, PyGithub and ipdb.

Then run it from the command line.

Note: If I were to do a migration again, I'd modify the script to make the
import note a comment instead of a part of the description, and I'd run the
migration as a dedicated 'migrationbot' user.

Caution: Be prepared for errors. Try it out on a fresh repo which you can
easily kill again.

Hint: If you want to migrate all issues, it's a wise choice to start with a
GitHub repo without any issues and actually migrate all issues. That way,
number references in code and other issues will be kept functional.
"""

BB_USER = u'from_user'
BB_REPO = u'from_repo'

GH_USER = u'to_user'
GH_REPO = u'to_repo'

# Github authentication token
# 
# Get one with the following command - username needs write access on
# the github repo specified above.
#
# curl -u 'username' -d '{"scopes":["repo"],"note":"Migration"}' \
#     https://api.github.com/authorizations
#

GH_TOKEN = '1234567890abcdef1234567890abcdef12345678'

# map bitbucket usernames to github usernames.
# all assignees of bitbucket issues should appear here.

USER_MAP = {
    u'bb_username': u'gh_username',
}


CONTENT_TEMPLATE = u"""{content}


**Note**: This {content_type} has been automatically migrated from Bitbucket
Created by {author} on {utc_created_on}"""


from bitbucket import BitBucket
from github import Github
gh = Github(GH_TOKEN)

_gh_users = {}


def get_gh_user(username):
    if username not in _gh_users:
        _gh_users[username] = gh.get_user(username)
    return _gh_users[username]


def append_migrate_suffix(content_type, content, username, created, updated):

    if username is None:
        author = u'Anonymous'
    elif username in USER_MAP:
        author = u'@%s' % USER_MAP[username]
    else:
        author = u'[%s](https://bitbucket.org/%s)' % (2 * (username,))

    text = CONTENT_TEMPLATE.format(
        content_type=content_type,
        content=content,
        author=author,
        utc_created_on=created
    )

    if updated != created:
        text += u', last updated: %s' % updated

    return text

gh_repo = get_gh_user(GH_USER).get_repo(GH_REPO)

_gh_repo_labels = dict([(l.name, l) for l in list(gh_repo.get_labels())])


def get_gh_label(label):
    if label not in _gh_repo_labels:
        _gh_repo_labels[label] = gh_repo.create_label(label, '444444')
    return _gh_repo_labels[label]


class GithubIssue(object):

    def __init__(self, bb_issue, create=False):

        self.title = ''
        self.body = None
        self.username = None
        self.assignee = None
        self.closed = False
        self.labels = set()
        self.comments = []

        self.update(bb_issue.get())
        self.add_comments(bb_issue.comments())

        if create:
            self.gh_create()

    def update(self, data):

        # status: new, open, resolved, on hold

        if data['status'] == u'resolved':
            self.closed = True

        self.title = data[u'title']

        print 'Fetched issue "%s"' % self.title

        # priority: trivial, minor, major, critical, blocker
        self.labels.add(u'prio-%s' % data[u'priority'])

        # metadata['kind']: bug, enhancement, proposal, task
        self.labels.add(u'type-%s' % data[u'metadata'][u'kind'])

        if data[u'metadata'][u'component'] is not None:
            self.labels.add(u'component-%s' % data[u'metadata'][u'component'])

        if u'responsible' in data:
            self.assignee = USER_MAP[data[u'responsible'][u'username']]

        if u'reported_by' in data:
            self.username = data[u'reported_by'][u'username']

        self.body = append_migrate_suffix(
            content_type='issue',
            content=data[u'content'],
            username=self.username,
            created=data[u'utc_created_on'],
            updated=data[u'utc_last_updated'],
        )

    def add_comments(self, comments):
        comments.reverse()

        for comment in comments:
            if comment['content'] is not None:
                if u'author_info' in comment and comment[u'author_info']:
                    username = comment[u'author_info'][u'username']
                else:
                    username = None

                body = append_migrate_suffix(
                    content_type='comment',
                    content=comment[u'content'],
                    username=username,
                    created=comment[u'utc_created_on'],
                    updated=comment[u'utc_updated_on']
                )

                self.comments.append(body)

    def gh_create(self):

        kwargs = {}

        if self.body is not None:
            kwargs[u'body'] = self.body

        if self.assignee is not None:
            kwargs[u'assignee'] = get_gh_user(self.assignee)

        kwargs[u'labels'] = map(get_gh_label, self.labels)

        issue = gh_repo.create_issue(self.title, **kwargs)

        for comment in self.comments:
            issue.create_comment(comment)

        if self.closed:
            issue.edit(state=u'closed')

        print 'Created issue "%s" - %s' % (self.title, issue.html_url)

        return issue


bb_repo = BitBucket().user(BB_USER).repository(BB_REPO)


def fetch_single(iid, create=False):
    return GithubIssue(bb_repo.issue(iid), create)


def fetch_multiple(low, high, create=False):
    return [fetch_single(iid, create) for iid in range(low, high + 1)]


def fetch_all(create=False):
    count = bb_repo.issues()['count']
    return fetch_multiple(1, count + 1, create)


def create_all(local_issues):
    for issue in local_issues:
        issue.gh_create()


print """

Do stuff like

Fetch a single issue do:

    i10 = fetch_single(10)

Create that issue on github:

    i10.gh_create()

Fetch and create multiple issues:

    ix = fetch_multiple(2, 5, create=True)

Fetch all issues do:

    all_issues = fetch_all()

Create them on github:

    create_all(all_issues)
"""

import ipdb
ipdb.set_trace()