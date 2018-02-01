#!/usr/bin/env python

# Copyright (c) 2014 Michael-Keith Bernard
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


"""
Pivotal Changelog Generator

Automatically generate changelog information from git commit history.

Usage:

# Get story information using simple formatting
changelog.py story_id story_d story_id ...

# Get story information for all stories named in a commit range
changelog.py --range=release20140201..release20140215

# Get story information in json format
changelog.py --json --range=foo..bar

# Get story information in yaml format
changelog.py --yaml --range=foo..bar

# Include only stories of a certain type
changelog.py --filter-type=bug,feature --range=foo..bar

# Use a custom formatting string
changelog.py --filter-type=feature --format="[#%(id)s] (%(estimate)s points) %(name)s" foo..bar

Note: Include Pivotal Tracker story ids in commit messages:

```
[#12345678] Add killer new feature

This commit is going to make us the next WhatsApp!
```

"""

__author__ = "Michael-Keith Bernard"

import re
import shlex
import urlparse
import argparse
import functools
import subprocess
from operator import itemgetter

import requests

STORY_REGEX = re.compile(r"(?:\[#?|\b)(\d{8})(?:\]|\b)")
PIVOTAL_PROJECT = "<project id>"
PIVOTAL_API_KEY = "<api key>"
PIVOTAL_API = "https://www.pivotaltracker.com/services/v5/"
PIVOTAL_URL = "https://www.pivotaltracker.com/"

STORY_FORMAT = """
Story Name: %(name)s
Story ID: %(id)s
Story URL: %(story_url)s
Points/Current State: (%(estimate)s) %(current_state)s
Labels: %(story_labels)s"""

### HELPER FUNCTIONS ###

def run(cmd):
    """Run local command and return output"""

    cmdp = shlex.split(cmd)
    return subprocess.check_output(cmdp, stderr=subprocess.STDOUT)

def memoize(fn):
    """Naive memoization decorator"""

    cache = {}
    @functools.wraps(fn)
    def wrapper(*args):
        if args not in cache:
            cache[args] = fn(*args)
        return cache[args]
    return wrapper

def group_by(fn, l):
    """Group elements of a list by grouping function"""

    acc = {}
    for e in l:
        key = fn(e)
        if key not in acc:
            acc[key] = [e]
        else:
            acc[key].append(e)
    return acc

def pluck(d, keys, default=None):
    """Extract keys from dict"""
    return { key: d.get(key, default) for key in keys
             if key in d or default is not None }

### PIVOTAL FUNCTIONS ###

def pivotal_story_url(story, project=PIVOTAL_PROJECT):
    """Pivotal API Story endpoint"""

    path = "/".join(["projects", str(project), "stories", str(story)])
    return urlparse.urljoin(PIVOTAL_API, path)

def pivotal_public_url(story):
    """Pivotal Web Story endpoint"""

    path = "/".join(["story", "show", str(story)])
    return urlparse.urljoin(PIVOTAL_URL, path)

@memoize
def get_story_info(story_id):
    """Fetch story metadata from Pivotal API

    Note: Multiple calls to the same story_id will be cached!
    """

    url = pivotal_story_url(story_id)
    resp = requests.get(url, headers={"X-TrackerToken": PIVOTAL_API_KEY})
    return resp.json() if resp.status_code == 200 else None

def get_stories(story_ids):
    """Lazily fetch story ids from Pivotal API"""

    for sid in sorted(story_ids):
        info = get_story_info(sid)
        if info:
            yield info

def get_stories_in_range(commit_range):
    """Find all Pivotal story ids in a git commit range"""

    git_log = run("git log --format=%%B %s" % commit_range)
    story_ids = set(int(sid.strip()) for sid in STORY_REGEX.findall(git_log))
    return story_ids

def format_stories(story_info, story_format=STORY_FORMAT):
    """Format Pivotal stories for a changelog"""

    for story_type, stories in story_info.iteritems():
        title = "%ss" % story_type.capitalize()
        print "\n%s\n%s" % (title, "=" * len(title))

        for story in stories:
            story.setdefault("estimate", "n/a")
            story["story_url"] = pivotal_public_url(story["id"])
            story["story_labels"] = ", ".join(l["name"] for l in story["labels"])
            print story_format % story

def main():
    parser = argparse.ArgumentParser(description="Changelog generator")
    parser.add_argument("--range", "-r", help="git commit range for changelog")
    parser.add_argument("stories", type=int, nargs="*", help="story ids")
    parser.add_argument("--format", "-f", default=STORY_FORMAT,
        help="changelog format")
    parser.add_argument("--filter-type", "-t", default="all",
        help="include only stories matching type")
    parser.add_argument("--json", "-j", action="store_true",
        help="return the raw story data as json")
    parser.add_argument("--yaml", "-y", action="store_true",
        help="return the raw story data as yaml")

    args = parser.parse_args()
    commit_range = args.range
    story_format = args.format
    story_types = set(t.strip().lower() for t in args.filter_type.split(","))

    if commit_range:
        stories = get_stories_in_range(commit_range)
    else:
        stories = args.stories

    by_type = group_by(itemgetter("story_type"), get_stories(stories))
    if "all" not in story_types:
        by_type = pluck(by_type, story_types, [])

    if args.json:
        import json
        print json.dumps(by_type, sort_keys=True)
    elif args.yaml:
        import yaml
        print yaml.safe_dump(by_type, default_flow_style=False)
    else:
        format_stories(by_type, story_format)

if __name__ == "__main__":
    main()
