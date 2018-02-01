import re
import sys
import csv
import json
import urllib2

from datetime import datetime

from collections import defaultdict as dd

DATE_FORMAT = "%m-%d-%Y"
NOTE_FORMAT = re.compile(r"(.*) \((.*) - (.*)\)", re.DOTALL)
P_NUMBER_FORMAT = re.compile(r"\[P#:(\d+)\]")
MONTHS = {'Jan': 1,
          'Feb': 2, 
          'Mar': 3, 
          'Apr': 4, 
          'May': 5, 
          'Jun': 6, 
          'Jul': 7, 
          'Aug': 8, 
          'Sep': 9, 
          'Oct': 10, 
          'Nov': 11, 
          'Dec': 12}

def todatetime(s):
    # Using %b to change the month is harder than expected
    # so I'm doing this the manual way.
    fields = s.split()
    month = MONTHS[fields[0]]
    day = int(fields[1].strip(', '))
    year = int(fields[2])
    return datetime(year, month, day)

def today():
    # can't compare date and datetime so I'm gonna simulate them
    return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

def buildauthormap(f):
    d = {}
    for line in open(f, 'rb'):
        if not line.strip(): continue
        
        aliases, credentials = line.strip().split(":")
        for alias in aliases.split(","):
            alias = alias.strip()
            if alias in d:
                raise Exception("%s alias appears in different accounts" % (alias,))
            username, password = credentials.strip().split(",")
            d[alias] = dict(username=username.strip(), password=password.strip())
    d[''] = dict(username="", password="")  # set a default for non assigned tickets
    return d

def togithubissue(d, authormap):
    body = "Pivotal Issue: %s\n\n%s" % (d['URL'][0], d['Description'][0])
    return {'title': "[P#:%s] %s" % (d['Id'], d['Story'][0]),
            'body': body,
            'assignee': authormap[d['Owned By'][0]]['username'],
            'labels': d['Labels']}

def togithubcomment(d):
    body = "%s\n\n%s" % (d['date'].strftime(DATE_FORMAT), d['Note'])
    return {"body": body}

def main(o):
    """
    I run the show.

    * Build a dictionary of PT issues from the csv file.
    * Removes issues that are finished
    * Creates an issue map with the issues already in the github project
    * Creates issues or comments depending on what you picked through arguments

    It doesn't keep track of which comments were created so that one should run
    fine immediately.

    Problem: You either get the passwords of all your users or you'll have to
    agree with them to run the file one by one first on all the issues and then
    on all the comments one by one, or you'll need to change this script to use
    OAuth2. In case you don't have OAuth2 you'll also have issues in comment
    ordering. This is why we leave a date in the comment body.
    """
    heads = None
    issues = {}
    authormap = buildauthormap(o.authormap)
    for i, line in enumerate(csv.reader(open(o.pivotal_file, 'rb'))):
        if not i:
            heads = line
            continue

        d = dd(lambda : [])
        for head, field in zip(heads, line):
            if head == "Note":
                if not field:
                    continue
                body, author, created_date = NOTE_FORMAT.match(field).groups()
                field = {'Note': body,
                         'author': author,
                         'date': todatetime(created_date)}

            d[head].append(field)

        issues[d['Id'][0]] = d

    # Take out closed issues, you can't really created closed issues in github and
    # pivotal tracker doesn't really change the status of tickets that were already
    # done in an iteration except that they have iteration end set.
    issues = dict((id, issue)
                    for id, issue in issues.iteritems()
                      if (not issue['Iteration End'][0] or
                          todatetime(issue['Iteration End'][0]) > today()))

    # Issues are created to have the pivotal tracker id in the title so that we can map
    # created ones to already to be created ones and avoid re-creating them.
    issuesmap = get_issues_map(o.base_url, authormap, o.github_username)
    
    if o.do_comments:
        for i, (issue_id, issue) in enumerate(issues.iteritems()):
            for note in issue['Note']:
                github_comment = togithubcomment(note)
                if not note['author']:
                    raise Exception("Unknown author of comment: %s" % (note,))
                credentials = authormap[note['author']]
                if credentials['password'] == "password":
                    print "Skipping comment to issue %s from user %s" % (
                        issue_id, note['author'])
                    continue

                github_issue_id = issuesmap[issue_id]
                sendcomment(o.base_url, github_comment, credentials, github_issue_id)
    else:
        for i, (issue_id, issue) in enumerate(issues.iteritems()):
            if issue_id in issuesmap:
                continue

            github_issue = togithubissue(issue, authormap)
            if not issue['Requested By'][0]:
                raise Exception("Unknown author of issue: %s" % (github_issue,))
            credentials = authormap[issue['Requested By'][0]]
            if credentials['password'] == "password":
                print "Skipping issue %s from user %s" % (
                    issue_id, issue['Requested By'][0])
                continue
            sendissue(o.base_url, github_issue, credentials)
        
def sendissue(base_url, github_issue, credentials):
    data = json.dumps(github_issue)

    try:
        indata = get_page("POST", base_url, credentials, data)
        print "Created issue", json.loads(indata)[number]

    except Exception, e:
        print e
        return None

def sendcomment(base_url, github_comment, credentials, github_issue_id):
    data = json.dumps(github_comment)

    try:
        indata = get_page("POST", "%s/%s/comments" % (
                base_url, github_issue_id), credentials, data)

    except Exception, e:
        print e
        return None
    
def get_page(method, url, credentials, data=None, and_response=False):
    import httplib
    import base64
    base64string = base64.encodestring('%(username)s:%(password)s' % credentials)[:-1]
    headers = {"Authorization": "Basic %s" % base64string}
    conn = httplib.HTTPSConnection("api.github.com")
    conn.request(method, url, data, headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    if response.status != 200:
        raise Exception("Couldn't fetch %s with status %s, response %s" % (
                url, response.status, data))
    if and_response:
        return response, data
    return data

def get_issues_map(base_url, authormap, github_username):
    # find credentials for this query
    for credentials in authormap.values():
        if credentials['username'] == github_username:
            break
    else:
        raise Exception("%s is not in the authormap, can't determine github password" % (
                github_username))

    issues = []
    current_page = 1
    while True:
        response, data = get_page("GET", base_url + "?page=%s" % (current_page,),
                                  credentials, and_response=True)
        issues.extend(json.loads(data))
        
        link_header = response.getheader("Link", None)

        # It appears that github puts the 'last' link unless you're in the last page
        if '; link="last"' not in link_header:
            break

        current_page += 1    

    d = {}
    for issue in issues:
        old_ticket = P_NUMBER_FORMAT.match(issue['title'])
        if not old_ticket:
            continue

        d[old_ticket.groups()[0]] = issue['number']
    return d
        
if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(prog="pivotal.py")

    aa = parser.add_argument

    aa("--authormap", action="store", dest="authormap", required=True,
       help=("Map of authors with corresponding username/password for GitHub "
             "Formatted one per line as: 'PT_user_label:gh_username,gh_password' "
             "gh_password should be 'password' if you want to skip the user"))

    aa("--pivotal-file", action="store", dest="pivotal_file",
       help="csv of exported pivotal data", required=True)
    
    aa("--base-github-url", action="store", dest="base_url", required=True,
       help="Base url for the github repo, such as /repos/:user/:repo/issues")

    aa("--do-comments-instead", action="store_true", dest="do_comments",
       help="import comments from pivotal to github")

    aa("--github-username", action="store", dest="github_username", required=True,
       help="Your GitHub username to fetch issues list for a project")
    
    args = parser.parse_args()

    print main(args)
