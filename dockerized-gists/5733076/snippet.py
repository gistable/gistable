#!/usr/bin/env python
""" Print all of the clone-urls for a GitHub organization.

It requires the pygithub3 module, which you can install like this::

    $ sudo yum -y install python-virtualenv
    $ mkdir scratch
    $ cd scratch

    $ virtualenv my-virtualenv
    $ source my-virtualenv/bin/activate

    $ pip install pygithub3

Usage example::

    $ python list-all-repos.py

Advanced usage.  This will actually clone all the repos for a
GitHub organization or user::

    $ for url in $(python list-all-repos.py); do git clone $url; done

"""

import pygithub3

gh = None


def gather_clone_urls(organization, no_forks=True):
    all_repos = gh.repos.list(user=organization).all()
    for repo in all_repos:

        # Don't print the urls for repos that are forks.
        if no_forks and repo.fork:
            continue

        yield repo.clone_url


if __name__ == '__main__':
    gh = pygithub3.Github()

    clone_urls = gather_clone_urls("FOSSRIT")
    for url in clone_urls:
        print url