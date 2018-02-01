import requests
import json
import sys
import csv


def getIssues(url):
    """
    @param {url} The url of the github issues
    @return the json object
    """
    r = requests.get(url)
    if r.status_code != 200:
        raise "There call to the GitHub issues API failed"
    return r.json()


def cleanIssues(issues):
    """
    @param {issues} the json object
    @returns {issues} with *only* the Title and Body
    """
    response = []
    for issue in issues:
        response.append({"title": issue["title"], "body": issue["body"]})
    return response


def dumpToCSV(issues):
    """
    @param {issues} the json object
    @returns True when complete
    """
    writer = csv.DictWriter(sys.stdout, ['title', 'body'])
    writer.writeheader()
    for issue in issues:
        writer.writerow({'title': issue["title"], 'body': issue["body"]})
    return True


if __name__ == "__main__":
    url = "https://api.github.com/repos/18F/bpa-fedramp-dashboard/issues?state=open"
    issues = getIssues(url)
    cleaned = cleanIssues(issues)
    dumpToCSV(cleaned)
