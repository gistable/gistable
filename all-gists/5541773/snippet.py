#!/usr/bin/python
# -*- coding: utf-8 -*-

# This script came about after I removed several big files from a GitHub
# repository (see https://gist.github.com/agarny/5541082) and force pushed
# everything back to GitHub. However, cloning the 'new' GitHub repository still
# results in those big files being present in the git history. This is, among
# other things, due to some pull requests I have in that repository and which
# reference those big files. I contacted GitHub about this, but there seems to
# be nothing that they can do about it. So, I was left with no other choice but
# to create a new repository and force push everything to it. To clone that new
# repository results in a local repository without all those big files, so
# that's good. However, all the features of the original GitHub repository are
# obviously gone. Some of those features simply cannot be imported (e.g. pull
# requests, watchers, stargazers, forks), but issues can (to some extent; see
# limitations below) and this is what this Python script does. It is based on
# the work on the Python script of Max Korenkov:
#
#    https://github.com/mkorenkov/tools/blob/master/gh-issues-import/gh-issues-import.py
#
# However, the script didn't work for me (e.g. closed issues were not imported),
# so I came up with the below script. It's my very first Python script, so I am
# sure it could be improved. Otherwise, though the script works fine with my
# GitHub repository, it may need some tweaking to work with yours. At least, set
# the configuration settings below.
#
# What the script does:
#  - Clean up the destination repository:
#     - Remove all existing milestones from the destination repository; and
#     - Remove all existing labels from the destination repository.
#  - Import the settings of the source repository to the destination repository:
#     - Import the source milestones to the destination repository;
#     - Import the source labels to the destination repository; and
#     - Import, in the order in which they were originally created, the source
#       issues (both open and closed) to the destination repository:
#        - Create the issue (incl. its title and body and, if any, its assignee,
#          milestone and labels);
#        - Import the comments associated with the issue, if any; and
#        - Close the issue, if needed.
#
# What the script does not (either due to GitHub API limitations or GitHub's
# 'features'):
#  - During the cleaning up of the destination repository, existing issues are
#    not removed. Indeed, once created, an issues simply cannot be deleted.
#  - Any imported issue can only be created on your behalf rather than that of
#    the original creator (unless it is you!). So, the best we can do, if you
#    are not the original creator, is to edit the issue's body and mention its
#    original creator.
#  - As for an imported issue, any comment for an imported issue will be created
#    on your behalf, but as for an imported issue we can, if needed, edit it and
#    mention its original creator.

import base64
import json
import urllib2

import StringIO

#=== Configuration ===
gitaccount = "octocat"
username = "octocat@github.com"
password = "octocat"
sourceRepository = "octocat/octocat"
destinationRepository = "octocat/newoctocat"
#=== End of configuration ===

server = "api.github.com"
sourceUrl = "https://%s/repos/%s" % (server, sourceRepository)
destinationUrl = "https://%s/repos/%s" % (server, destinationRepository)

leadingSpace = ""

def incrementOutput():
    global leadingSpace

    leadingSpace = leadingSpace+"   "

def decrementOutput():
    global leadingSpace

    leadingSpace = leadingSpace[3:]

def output(string = ""):
    print "%s%s" % (leadingSpace, string)

def openUrl(method, url, data = None):
    request = urllib2.Request(url, data)

    request.add_header("Authorization", "Basic " + base64.urlsafe_b64encode("%s:%s" % (username, password)))
    request.add_header("Content-Type", "application/json")
    request.add_header("Accept", "application/json")
    request.get_method = lambda: method

    response = urllib2.urlopen(request)
    data = response.read()

    if data:
        result = json.load(StringIO.StringIO(data))
    else:
        result = []

    return result

def getInformation(url):
    information = []
    maximumPerPage = 100

    if "?" in url:
        realUrl = url+"&page=%s&per_page=%s"
    else:
        realUrl = url+"?page=%s&per_page=%s"

    mustGetInformation = True
    page = 1

    while mustGetInformation:
        pageInformation = openUrl("GET", realUrl % (page, maximumPerPage))

        information.extend(pageInformation)

        if len(pageInformation) == maximumPerPage:
            page += 1
        else:
            mustGetInformation = False

    return information

def setInformation(method, url, data = None):
    openUrl(method, url, data)

def getMilestones(url):
    openMilestones = getInformation("%s/milestones?direction=asc" % url)
    closedMilestones = getInformation("%s/milestones?direction=asc&state=closed" % url)

    return openMilestones+closedMilestones

def getLabels(url):
    return getInformation("%s/labels" % url)

def getTypeOfIssues(url, status):
    return getInformation("%s/issues?direction=asc&state=%s" % (url, status))

def getIssues(url):
    openIssues = getTypeOfIssues(url, "open")
    closedIssues = getTypeOfIssues(url, "closed")

    issues = []

    for issueNumber in range(len(openIssues)+len(closedIssues)):
        for issue in openIssues+closedIssues:
            if issueNumber == issue["number"]-1:
                issues.append(issue)

                break

    return issues

def cleanUpMilestones(url):
    milestones = getMilestones(url)

    if milestones:
        output(" - Removing existing milestone(s):")

        incrementOutput()

        for milestone in milestones:
            setInformation("DELETE", "%s/milestones/%s" % (url, milestone["number"]))

            output(" - %s" % milestone["title"])

        decrementOutput()
    else:
        output(" - No milestones")

def cleanUpLabels(url):
    labels = getLabels(url)

    if labels:
        output(" - Removing existing label(s):")

        incrementOutput()

        for label in labels:
            setInformation("DELETE", "%s/labels/%s" % (url, label["name"]))

            output(" - %s" % label["name"])

        decrementOutput()
    else:
        output(" - No labels")

def cleanUp(url):
    cleanUpMilestones(url)
    cleanUpLabels(url)

def importMilestones(fromUrl, toUrl):
    milestones = getMilestones(fromUrl)

    if milestones:
        output(" - Importing milestone(s):")

        incrementOutput()

        for milestone in milestones:
            data = json.dumps({
                "title": milestone["title"],
                "state": milestone["state"],
                "description": milestone["description"],
                "due_on": milestone["due_on"]
            })

            setInformation("POST", "%s/milestones" % toUrl, data)

            output(" - %s" % milestone["title"])

        decrementOutput()

def importLabels(fromUrl, toUrl):
    labels = getLabels(fromUrl)

    if labels:
        output(" - Importing label(s):")

        incrementOutput()

        for label in labels:
            data = json.dumps({
                "name": label["name"],
                "color": label["color"]
            })

            setInformation("POST", "%s/labels" % toUrl, data)

            output(" - %s" % label["name"])

        decrementOutput()

def importIssues(fromUrl, toUrl):
    issues = getIssues(fromUrl)

    if issues:
        milestones = getMilestones(toUrl)

        output(" - Importing issue(s):")

        incrementOutput()

        for issue in issues:
            # Create the issue

            issueBody = ""

            if issue["user"]["login"] != gitaccount:
                issueBody += "**Note:** this issue was imported, but it was originally created by [%s](https://github.com/%s)...\n\n" % (issue["user"]["login"], issue["user"]["login"])

            issueBody += issue["body"]

            if issue["assignee"]:
                assigneeLogin = issue["assignee"]["login"]
            else:
                assigneeLogin = None

            milestoneNumber = None

            if issue["milestone"]:
                for milestone in milestones:
                    if issue["milestone"]["title"] == milestone["title"]:
                        milestoneNumber = milestone["number"]

                        break
            labelsArray = []

            if issue["labels"]:
                for label in issue["labels"]:
                    labelsArray.append(label["name"])

            data = json.dumps({
                "title": issue["title"],
                "body": issueBody,
                "assignee": assigneeLogin,
                "milestone": milestoneNumber,
                "labels": labelsArray
            })

            setInformation("POST", "%s/issues" % toUrl, data)

            output(" - Issue #%s (by %s) [%s]: %s" % (issue["number"], issue["user"]["login"], issue["state"], issue["title"]))

            # Add comments to the issue, if any

            comments = getInformation("%s/issues/%s/comments" % (fromUrl, issue["number"]))

            if comments:
                incrementOutput()

                commentNumber = 0

                for comment in comments:
                    commentBody = ""

                    if comment["user"]["login"] != gitaccount:
                        commentBody += "**Note:** this comment was imported, but it was originally made by [%s](https://github.com/%s)...\n\n" % (comment["user"]["login"], comment["user"]["login"])

                    commentBody += comment["body"]

                    data = json.dumps({
                        "body": commentBody
                    })

                    setInformation("POST", "%s/issues/%s/comments" % (toUrl, issue["number"]), data)

                    commentNumber += 1

                    output(" - Comment #%s (by %s)" % (commentNumber, comment["user"]["login"]))

                decrementOutput()

            # Close the issue, if needed

            if issue["state"] == "closed":
                data = json.dumps({
                    "state": issue["state"]
                })

                setInformation("PATCH", "%s/issues/%s" % (toUrl, issue["number"]), data)

        decrementOutput()

def importSettings(fromUrl, toUrl):
    importMilestones(fromUrl, toUrl)
    importLabels(fromUrl, toUrl)
    importIssues(fromUrl, toUrl)

def main():
    output("Cleaning up %s:" % destinationRepository)

    cleanUp(destinationUrl)

    output()
    output("Importing settings of %s to %s:" % (sourceRepository, destinationRepository))

    importSettings(sourceUrl, destinationUrl)

if __name__ == '__main__':
    main()
