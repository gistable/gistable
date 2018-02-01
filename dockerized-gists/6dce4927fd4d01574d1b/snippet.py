#!/usr/bin/env python
#
# 1. Save this file as `pre-commit` in your local .git/hooks/ directory
# 2. Make sure your file is executable `chmod +x pre-commit`
# Upon git commit, this script will check your staged files against your eslint ruleset
# More flags and options at http://eslint.org/

import os, sys

"""
Checks your git commit with eslint. Only checks staged files
"""
def eslint():
    
    errors = []
    
    # get all staged files
    f = os.popen('git diff --cached --name-only --diff-filter=ACM')
    
    for file in f.read().splitlines():

        # makes sure we're dealing javascript files
        if file.endswith('.js') and not file.startswith('node_modules/'):     

            g = os.popen('eslint ' + file)
        
            # add all errors from all files together
            for error in g.readlines():
                errors.append(error)
    
    # got errors?
    if errors:
        for i, error in enumerate(errors):
            print error,
    
        # Abort the commit
        sys.exit(1) 
    
    # All good
    sys.exit(0) 
    
if __name__ == '__main__':
    eslint()