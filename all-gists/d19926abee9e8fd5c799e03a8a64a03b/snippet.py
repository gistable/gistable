""" github_orgy -- monitor github organizations for new repos.
Usage:
python3.5 github_orgy.py deepmind tensorflow facebookresearch google watson-developer-cloud

Or with cron:
@hourly /usr/bin/python github_orgy.py deepmind tensorflow facebookresearch google watson-developer-cloud
"""

import time
import os
import sys
import re

# Works with Python 2 and 3
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

BASE_PATH = os.path.expanduser("~/github_orgy")
HTML_STOP_TEXTS = ["This organization has no more repositories.",
                   "doesn’t have any repositories you can view"]
SLEEP_FOR_SECONDS = 3
VERBOSE = True


def notify(org, repos):
    # Implement your notification logic here
    # # 1. print
    for repo in repos:
        print("Send email/save/whatever org: {}, repo: '{}'".format(org, repo))
    # # 2. email (pip install yagmail / https://github.com/kootenpv/yagmail)
    # import yagmail
    # yag = yagmail.SMTP("username", "password")
    # yag.send(subject="New repo(s) in github org '{}'".format(org),
    #          contents=["https://github.com/{}/{}".format(org, x) for x in repos])


def get_org_path(org):
    return os.path.join(BASE_PATH, org + ".txt")


def setup_first_scan(org_path):
    first_scan = False
    if not os.path.isfile(org_path):
        if VERBOSE:
            print("Creating '{}'".format(org_path))
        open(org_path, "w").close()
        first_scan = True
    return first_scan


def get_known_repos(org):
    org_path = get_org_path(org)
    known_repos = []
    if os.path.isfile(org_path):
        with open(org_path) as f:
            known_repos = [line.strip() for line in f if line.strip()]
    return set(known_repos)


def get_repos_from_page(html):
    # When github updates the website, this is the line we will have to update
    finder = re.compile('itemprop="name codeRepository">([^<]+)</a>', flags=re.MULTILINE)
    repos = [x.strip() for x in finder.findall(html)]
    return repos


def to_file(org_path, new_repos):
    with open(org_path, "a") as f:
        f.write("\n".join(new_repos) + "\n")


def monitor_org(org):
    org_path = get_org_path(org)

    first_scan = setup_first_scan(org_path)
    limit_num_pages = 50 if first_scan else 1

    num_page = 1
    new_repos = []
    known_repos = get_known_repos(org)
    # loop for 1 (incremental) or 10 pages (initial)
    while num_page < limit_num_pages + 1:
        if num_page > 1:
            time.sleep(SLEEP_FOR_SECONDS)
        if VERBOSE:
            print("Getting repos from page", num_page)
        url = "https://github.com/{}?page={}".format(org, num_page)
        html = urlopen(url).read().decode("utf8")
        repos_from_page = get_repos_from_page(html)
        new_repos.extend([x for x in repos_from_page if x not in known_repos])

        if any([stop_text in html for stop_text in HTML_STOP_TEXTS]):
            break

        num_page += 1

    if not new_repos:
        return

    notify(org, new_repos)

    to_file(org_path, new_repos)


def main():
    if not os.path.isdir(BASE_PATH):
        if VERBOSE:
            print("Creating '{}' directory".format(BASE_PATH))
        os.makedirs(BASE_PATH)
    for org in sys.argv[1:]:
        if VERBOSE:
            print("Monitoring '{}'".format(org))
        monitor_org(org)
        time.sleep(SLEEP_FOR_SECONDS)


if __name__ == "__main__":
    main()
