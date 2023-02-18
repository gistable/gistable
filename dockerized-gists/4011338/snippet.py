#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import subprocess

def updateGit():
    cwd = os.getcwd()
    git = os.path.abspath(os.path.join(cwd, '.git'))
    myURLs = r'https://github.com/RoyXiang/', r'git@github.com:RoyXiang/'

    if os.path.exists(git):
        if os.path.isdir(git):
            config = os.path.join(git, 'config')
        else:
            gitfile = open(git, 'r')
            for line in gitfile:
                gitdir = re.match(r'^gitdir\:\s*(.*)$', line)
                if gitdir != None:
                    config = os.path.join(cwd, line[gitdir.start(1):gitdir.end(1)], 'config')
                    break
        config = os.path.abspath(config)
    else:
        print 'This is not a git foler!'
        return

    lines = open(config, 'r').readlines()
    for i in range(len(lines)):
        part = re.match(r'^\[([\w]+)(?:\s"([^\]]+)")?\]$', lines[i])
        if part != None:
            i = i + 1
            if part.group(1) == 'remote':
                while True:
                    url = re.match(r'^\s*url\s*=\s*([^\s]+)$', lines[i])
                    if url != None:
                        if not (lines[i][url.start(1):url.end(1)]).startswith(myURLs):
                            if part.group(2) == 'origin':
                                subprocess.call(['git', 'pull'])
                            else:
                                subprocess.call(['git', 'fetch', part.group(2)])
                                subprocess.call(['git', 'merge', part.group(2) + '/main'])
                        break
                    else:
                        i = i + 1
            elif part.group(1) == 'submodule':
                url = re.match(r'^\s*url\s*=\s*([^\s]+)$', lines[i])
                print 'Entering \"' + part.group(2) + '\"'
                path = os.path.abspath(os.path.join(cwd, part.group(2)))
                os.chdir(path)
                updateGit()
                os.chdir(cwd)

if __name__ == '__main__':
    updateGit()
