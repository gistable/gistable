#!/usr/bin/env python
# encoding: utf-8
import sys
import subprocess


def convert_git_url(git_url):
    if git_url.startswith('git@'):
        git_url = 'http://' + '/'.join(git_url[4:].split(':'))
    return git_url


def get_url(name='origin'):
    try:
        out = subprocess.check_output(['git', 'remote', '-v'])
    except subprocess.CalledProcessError:
        return None

    for line in out.splitlines():
        remote_name, git_url = line.split()[:2]
        if remote_name == name:
            return convert_git_url(git_url)

    print 'fatal: Cannot find a repo named %s' % name
    return None


def main():
    url = get_url(sys.argv[1]) if len(sys.argv) >= 2 else get_url()
    if url is None:
        return 1
    else:
        return subprocess.call(['open', url])


if __name__ == '__main__':
    sys.exit(main())