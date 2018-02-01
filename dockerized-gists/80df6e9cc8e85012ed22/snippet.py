import json
import requests
from requests.auth import HTTPBasicAuth
from sys import argv

url = "https://tickets.puppetlabs.com/rest/api/2/issue/{jira_issue_number}/remotelink"
headers = {'Content-type': 'application/json'}
auth = HTTPBasicAuth('ian.kronquist', 'your jira password')


def make_request():
    gh_issue_number =  argv[2]
    jira_issue_number =  argv[1]

    jira_issue_number = 'PDOC-{}'.format(jira_issue_number)
    title = 'GitHub #{}'
    name = 'https://github.com/puppetlabs/puppetlabs-strings/pull/{}'

    data = { "object": { "url": name.format(gh_issue_number), "title": title.format(gh_issue_number)} }
    data = json.dumps(data)
    print data

    r = requests.post(url.format(jira_issue_number=jira_issue_number), auth=auth, headers=headers, data=data)
    print r.content


if __name__ == "__main__":
    if len(argv) != 3:
        print("Links a Jira issue to GitHub PR.\n" +
            "jiralink.py jira_issue_number github_issue_number ")
        exit()
    else:
        make_request()
