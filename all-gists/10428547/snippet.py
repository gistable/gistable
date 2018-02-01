from collections import defaultdict
from functools import partial

import sys

try:
    from github import Github
except ImportError:
    print "Install PyGithub: sudo pip install PyGithub"
    sys.exit(-1)

# Counters
closed_issues = 0
missed_issues = 0

# Connect to Github using access token
gh = Github(login_or_token='GITHUB-ACCESS-TOKEN-GOES-HERE')

# Repository
robottelo = gh.get_repo('omaciel/robottelo')

# Milestone
sprint = robottelo.get_milestone(8)

# All Issues
issues = list(robottelo.get_issues(milestone=sprint, state='all'))

sprint_data = defaultdict(partial(defaultdict, list))

for issue in issues:
    try:
        name = issue.assignee.login
    except Exception:  # issue is not assigned to anyone
        name = u'unassigned'
    status = issue.state
    url = issue.html_url

    # Gives you {'Bob': {'open': [], 'closed': []}}
    sprint_data[name][status].append(url)

# Print data

print "  * %s: %s" % (sprint.title, sprint.url)

for assignee in sprint_data:
    # Extract closed/missed issues
    closed = len(sprint_data[assignee]['closed'])
    missed = len(sprint_data[assignee]['open'])

    # Update totals
    closed_issues += closed
    missed_issues += missed

    # Assignee status
    print "    * %s: ( Closed: %d / Missed: %d)" % (assignee, closed, missed)

    # Issues and status per assignee
    for issue_status in sprint_data[assignee].keys():
        for issue_url in sprint_data[assignee][issue_status]:
            print "      * %s - [%s]" % (issue_url, issue_status.upper())

# Print totals
print "  * Closed: %d" % closed_issues
print "  * Missed: %d" % missed_issues
print "  * TOTAL: %d" % (closed_issues + missed_issues)