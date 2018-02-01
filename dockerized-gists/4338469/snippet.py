#!/usr/bin/env python


import json
import os
import urllib


"""Download latest source release from PyPI.

package must have a source tarball hosted on PyPI.
"""


PACKAGES = [
    'Django',
    'flake8',
    'nose',
]


def main():
    for package in PACKAGES:
        'retrieving %r...' % package
        tarball_url = get_latest_tarball_url(package)
        file_name = os.path.basename(tarball_url)
        print '  found: %s' % file_name
        urllib.urlretrieve(tarball_url, file_name)
        print '  saved: %s' % tarball_url


def get_latest_tarball_url(package):
    url = 'http://pypi.python.org/pypi/%s/json' % package
    f = urllib.urlopen(url)
    j = json.load(f)
    release_links = j['urls']
    tarball_url = sorted(
        [link['url'] for link in release_links
            if link['url'].endswith('.tar.gz')]
    )[0]
    return tarball_url


if __name__ == '__main__':
    main()
