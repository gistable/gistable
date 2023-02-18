#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""A post-update Git hook to execute `composer install` when composer.json changes

:Author: Cody Halovich
:Company: HootSuite Media Inc.
"""

import subprocess
import string
import os

HOOK_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(HOOK_DIR))

def getChangeList():
    """Retrieve the active Git change-list
    """
    files = subprocess.Popen(['git', 'diff', '--name-status', 'main@{1}'], stdout=subprocess.PIPE)
    results = files.stdout.read()
    return results

def main():
    """Update composer if `composer.lock` exists in the active change-list 
    """
    if getChangeList().find('composer.lock') > 0:
        os.chdir(ROOT_DIR)
        subprocess.Popen([ROOT_DIR + 'composer.phar', 'install'])

if __name__ == '__main__':
    main()