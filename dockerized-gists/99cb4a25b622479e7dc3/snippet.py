"""Grab version files from dist.plone.org for each Plone version.

Original location:
https://gist.github.com/mauritsvanrees/99cb4a25b622479e7dc3

Goal: grep through these files to see which version of a package is
used in which Plone version.

Usage:
$ virtualenv-2.7 .
$ bin/pip install requests
$ bin/python grabversions.py
"""
import os
import requests
import re
import sys

# Get directory listing
LIST = 'http://dist.plone.org/release/'
LATEST = '5.1'
IGNORE = [
    '4.0.6',  # There is a 4.0.6.1 release.
    '5.0a1',  # Empty release dir.
    ]
# File renames, for example to get same file length for all, or
# correct the sort order.
RENAMES = {
    '4.0.6.1.cfg': '4.0.6.cfg',
    '4.0.10.cfg': '4.0.t.cfg',
}

req = requests.get(LIST)
if req.status_code != 200:
    print('status code for {} is {}'.format(LIST, req.status_code))
    sys.exit(1)

# Search for this pattern in the text.
pat = re.compile('href="([^:/]*)/"')
for link in pat.findall(req.text):
    if '..' in link:
        continue
    if 'pending' in link:
        continue
    if link in IGNORE:
        continue
    # e.g. 4.2.7.cfg
    filename = link + '.cfg'
    # Only grab alpha, beta and rc for LATEST release.
    if ('a' in link or 'b' in link or 'rc' in link):
        if LATEST not in link:
            continue
    elif link.count('.') == 1:
        # 4.2 -> 4.2.0, to look nicer
        filename = link + '.0.cfg'
    # Possibly rename.
    filename = RENAMES.get(filename, filename)
    if os.path.exists(filename):
        continue
    print('Creating file {}'.format(filename))
    # Get e.g. http://dist.plone.org/release/4.2.7/versions.cfg
    url = LIST + link + '/versions.cfg'
    print('Getting url {}'.format(url))
    result = requests.get(url)
    if result.status_code != 200:
        print('status code for {} is {}'.format(url, result.status_code))
    else:
        with open(filename, 'w') as versionsfile:
            versionsfile.write(result.text)
