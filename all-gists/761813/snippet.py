#!/usr/bin/env python
# encoding: utf-8

""" Create a symlink of the current .git inside your Dropbox, now all your 
    local commits will automatically be backed up to Dropbox (without your dropbox
    being littered with development cruft, like temporary build files)
"""

from os import getcwd, path, mkdir, symlink, chdir

DROPBOXREPOBASE=path.expanduser('~/Dropbox/Development/git-repos/')

def main():
    if not path.exists('.git'):
        exit("No .git found in current directory.")
    parent = path.split(path.abspath('.'))[-1]
    target_path = path.join(DROPBOXREPOBASE, parent)
    if path.exists(target_path):
        exit("Directory already exists at %s, not touching it!" % target_path)
    mkdir(target_path)
    repo_path = path.abspath('.git')
    whereami = getcwd()
    chdir(target_path)
    symlink(repo_path, '.git')
    chdir(whereami)
    print("Created symlink at %s" % target_path)

if __name__ == '__main__':
    main()
