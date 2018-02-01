from __future__ import print_function

import json
from collections import defaultdict
import time
from datetime import datetime

import requests
import numpy as np


api_url = "https://api.github.com"


def pull_request(payload):
    if payload["action"] == "opened":
        return 0.9
    return 0.6


def issues(payload):
    if payload["action"] == "opened":
        return 0.6
    return 0.4


def push(payload):
    size = payload["size"]
    return 0.2 + 0.6 * min(size, 8) / 8.0


tau = 60 * 60 * 24 * 30.0

weights = {
        "CommitCommentEvent":               lambda payload: 0.6,
        "CreateEvent":                      lambda payload: 1.0,
        "DeleteEvent":                      lambda payload: 0.0,
        "DownloadEvent":                    lambda payload: 0.5,
        "FollowEvent":                      lambda payload: 0.3,
        "ForkEvent":                        lambda payload: 0.4,
        "ForkApplyEvent":                   lambda payload: 0.0,
        "GistEvent":                        lambda payload: 0.0,
        "GollumEvent":                      lambda payload: 0.9,
        "IssueCommentEvent":                lambda payload: 0.7,
        "IssuesEvent":                      issues,
        "MemberEvent":                      lambda payload: 1.0,
        "PublicEvent":                      lambda payload: 0.5,
        "PullRequestEvent":                 pull_request,
        "PullRequestReviewCommentEvent":    lambda payload: 0.9,
        "PushEvent":                        push,
        "TeamAddEvent":                     lambda payload: 1.0,
        "WatchEvent":                       lambda payload: 0.6,
        }


def parse_time(time_str):
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    dt = time.mktime(time.gmtime()) - time.mktime(time.strptime(time_str, fmt))
    return dt


def count_events(repo, page=0, maxpage=5):
    print("Getting page {0}".format(page))
    response = requests.get(api_url + "/repos/" + repo + "/events",
            params={"page": page})

    if response.status_code != 200:
        response.raise_for_status()

    data = json.loads(response.text)

    counts = defaultdict(float)
    for event in data:
        dt = parse_time(event["created_at"])
        factor = np.exp(-dt / tau)
        counts[event["actor"]["login"]] += \
                weights[event["type"]](event.get("payload", None)) \
                * factor

    if page < maxpage:
        next_page = count_events(repo, page=page + 1, maxpage=maxpage)
        for k, v in next_page.iteritems():
            counts[k] += v

    return counts


if __name__ == "__main__":
    counts = count_events("libgit2/libgit2")
    ordered = sorted(counts, key=counts.__getitem__)
    max_count = counts[ordered[-1]]
    for user in ordered:
        print(user, counts[user] / max_count)
