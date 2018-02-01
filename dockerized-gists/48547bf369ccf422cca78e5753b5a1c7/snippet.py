#!/user/bin/env python

#
# This is a simple python script to clone all of the repositories for an
# assignment managed via GitHub Classroom.  It has a dependency on the
# requests module, so to use it, you must:
#
#   pip install requests
#
# You can run the script with the '-h' option to get info on its usage.
#

import os
import re
import json
import textwrap
import subprocess as SP

import requests

from argparse import ArgumentParser

GRADING_TAG = '__graded_commit'
GRADING_BRANCH = '__grading_branch'

def clone_repos(repo_urls, output_dir, due_date=None):
    """
    Clone a set GitHub repositories into a specified output directory.

    :param repo_urls: A list of repository URLs to be cloned.  The URLs should
        have any needed authentication info embedded into them.
    :param output_dir: The directory in which to save the cloned repos.
    :param due_date: If not None, the last commit before this timestamp (in
        ISO-8601 format) is checked out.
    """

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i, repo_url in enumerate(repo_urls):

        repo_dir = os.path.splitext(repo_url.rsplit('/', 1)[1])[0]
        print "== cloning %4d of %4d: %s" % (i + 1, len(repo_urls), repo_dir)

        p = SP.Popen(['git', 'clone', repo_url, repo_dir], stdout=SP.PIPE, stderr=SP.PIPE, cwd=output_dir)
        out, err = p.communicate()

        if p.returncode != 0:
            print "  == clone failed with this output:"
            print "  == stdout:", out
            print "  == stderr:", err

        # If we have a due date specified, figure out the last commit before
        # the due date.  Otherwise, use the HEAD commit.
        if due_date:
            p = SP.Popen(['git', 'rev-list', '-n', '1', '--before', due_date, 'HEAD'],
                stdout=SP.PIPE, stderr=SP.PIPE, cwd=(output_dir + '/' + repo_dir))
            commit, _ = p.communicate()
            commit = commit.strip()
        else:
            commit = 'HEAD'

        # Tag the commit as being graded and check out a new grading branch.
        p = SP.Popen(['git', 'tag', '-a', GRADING_TAG, '-m', "Grading this commit.", commit],
            stdout=SP.PIPE, stderr=SP.PIPE, cwd=(output_dir + '/' + repo_dir))
        p.communicate()
        p = SP.Popen(['git', 'checkout', '-b', GRADING_BRANCH, commit],
            stdout=SP.PIPE, stderr=SP.PIPE, cwd=(output_dir + '/' + repo_dir))
        p.communicate()


def get_repo_urls(org, prefix, user, token):
    """
    Gets a list of all URLS for GitHub repos within an organization starting
    with a given prefix.

    :param org: The GitHub organization.
    :param prefix: The prefix by which to filter repo names.
    :param user: The GitHub username with which to authorize.
    :param token: The GitHub auth token/password with which to authorize.
    """

    # Helper function to incorporate username and token into clone URL via
    # regex matching (down below).
    def repl(m):
        _user = user if user else ''
        _token = ':%s' % token if token else ''
        _url_prefix = m.group(0)
        if _user:
            _url_prefix += _user + _token + '@'
        return _url_prefix

    org_repos_url = 'https://api.github.com/orgs/%s/repos' % org
    params = {'per_page': 100}
    page = 0

    repo_urls = set()
    while True:

        print "== fetching repo list, page %d" % page

        # Request the current page of repos.
        params['page'] = page
        resp = requests.get(org_repos_url, params=params, auth=(user, token))

        # For each repo whose name starts with prefix, add that repo's clone
        # URL into the set after incorporating the username and token into it.
        for repo in resp.json():
            if repo['name'].startswith(prefix):
                repo_urls.add(re.sub(r'(https?://)', repl, repo['clone_url']))

        # Stop if this page of repos was empty.
        if len(resp.json()) == 0:
            break

        page += 1

    return list(repo_urls)


def main(args):

    token = None
    if args.token_file:
        with open(args.token_file) as fh:
            token = fh.read().strip()

    repo_urls = get_repo_urls(args.ORG_NAME, args.ASSIGNMENT_PREFIX, args.user, token)
    clone_repos(repo_urls, args.OUTPUT_DIR, args.due_date)


if __name__ == '__main__':

    parser = ArgumentParser(description="Download GitHub Classroom repositories for a given assignment")
    parser.add_argument('ORG_NAME', help="Organization name for GitHub Classroom")
    parser.add_argument('ASSIGNMENT_PREFIX', help="Prefix string for the assignment.")
    parser.add_argument('OUTPUT_DIR', help="Directory in which to output cloned repos.")
    parser.add_argument('-d', '--due-date', help="Optional ISO-8601 timestamp corresponding to the assignment's due date.")
    parser.add_argument('-u', '--user', help="GitHub username.")
    parser.add_argument('-t', '--token-file', help="File containing GitHub authorization token/password.")
    args = parser.parse_args()

    main(args)
