#!/usr/bin/env python
# encoding: utf-8
import json
import os
import subprocess
import sys
import urllib2

from optparse import OptionParser

USAGE = "%prog <review_id>"

RB_URL = "https://git.reviewboard.kde.org"

DEBUG_JSON="DEBUG_JSON" in os.environ

def api_request(url):
    if DEBUG_JSON:
        print "DEBUG_JSON: Fetching", url
    fl = urllib2.urlopen(url)
    dct = json.load(fl)
    if DEBUG_JSON:
        print "DEBUG_JSON:"
        print json.dumps(dct, sort_keys=True, indent=4)
    return dct

def get_request_info(request_id):
    dct = api_request(RB_URL + "/api/review-requests/%d/" % request_id)
    return dct["review_request"]

def get_author_info(submitter_url):
    dct = api_request(submitter_url)
    return dct["user"]

def download_diff(request_id):
    fl = urllib2.urlopen(RB_URL + "/r/%d/diff/raw/" % request_id)
    return fl.read()

def git(*args):
    cmd = ["git"] + list(args)
    print "Running '%s'" % " ".join(cmd)
    return subprocess.call(cmd) == 0

def main():
    parser = OptionParser(usage=USAGE)

    parser.add_option("-b", "--branch",
                      action="store_true", dest="branch", default=False,
                      help="Create a branch named after the reviewboard id")

    (options, args) = parser.parse_args()

    if len(args) == 0:
        parser.error("Missing args")

    request_id = int(args[0])

    print "Fetching request info"
    request_info = get_request_info(request_id)
    summary = request_info["summary"]
    description = request_info["description"]

    author_info = get_author_info(request_info["links"]["submitter"]["href"])
    fullname = author_info.get("fullname")
    email = author_info.get("email")
    if fullname is None:
        default_fullname = author_info["username"]
        fullname = raw_input("Could not get fullname for user '%s'. Please enter it [%s]: " % (author_info["username"], default_fullname))
        if fullname == "":
            fullname = default_fullname
    if email is None:
        default_email = fullname + "@unknown.com"
        email = raw_input("Could not get email for user '%s'. Please enter it [%s]: " % (author_info["username"], default_email))
        if email == "":
            email = default_email
    author = "%s <%s>" % (fullname, email)

    print "Downloading diff"
    diff = download_diff(request_id)

    name = "rb-%d.patch" % request_id
    print "Creating %s" % name
    with open(name, "w") as f:
        print >>f, "From:", author.encode("utf-8")
        print >>f, "Subject:", summary.encode("utf-8")
        print >>f
        print >>f, description.encode("utf-8")
        print >>f
        f.write(diff)

    if options.branch:
        if not git("checkout", "-b", "rb-%d" % request_id):
            return 1

    if not git("am", name):
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
# vi: ts=4 sw=4 et
