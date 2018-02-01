#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import argparse
import getpass
import subprocess
import base64
import urllib2

"""
!!! set your public ssh key in your bitbucket account settings !!!s

~/$ python clonebb.py --help
usage: clonebb.py [-h] [-l LANGUAGE] [-d CLONE_DIR] account

positional arguments:
  account               bitbucket team/account name

optional arguments:
  -h, --help            show this help message and exit
  -l LANGUAGE, --language LANGUAGE
                        only clone projects written in this language
  -d CLONE_DIR, --clone-dir CLONE_DIR
                        dir to clone project(s)

"""

CLONE_DIR = None
CLONE_URL = 'git@bitbucket.org:{team}/{slug}.git'
TEAM_INFO_URL = 'https://bitbucket.org/!api/1.0/users/{team}'

def run_command(command, shell=True):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=shell)
    proc_stdout = process.communicate()[0].strip()
    return proc_stdout

def get_credentials():
    return raw_input('bitbucket username?\n'), getpass.getpass(prompt='bitbucket pass?\n')

def gti(team_name):
    username, password = get_credentials()
    auth = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    request = urllib2.Request(TEAM_INFO_URL.format(team=team_name))
    request.add_header("Authorization", "Basic %s" % auth)
    result = urllib2.urlopen(request)
    return json.loads(result.read())


def clone_repo(slug, team):
    run_command(
        'cd {clone_dir} && git clone {git_uri}'.format(
            git_uri=CLONE_URL.format(
                team=team,
                slug=slug
                ),
            clone_dir=CLONE_DIR
        )
    )

def main():
    global CLONE_DIR
    parser = argparse.ArgumentParser()
    parser.add_argument("account", help="bitbucket team/account name",
                        type=lambda s: unicode(s, 'utf8'))

    parser.add_argument("-l", "--language", help="only clone projects written in this language",
                        type=lambda s: unicode(s, 'utf8'))

    parser.add_argument("-d", "--clone-dir", help="dir to clone project(s)",
                        type=lambda s: unicode(s, 'utf8'), default='.')
    args = parser.parse_args()

    CLONE_DIR = args.clone_dir
    language = args.language
    team_info = gti(args.account)
    print "Cloning project(s)... "

    for project in team_info['repositories']:
        if language:
            if project['language'] != language:
                continue
        clone_repo(project['slug'], args.account)

    print "\nDone!"

if __name__ == '__main__':
    main()
