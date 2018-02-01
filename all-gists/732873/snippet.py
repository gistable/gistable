#!/usr/bin/env python
import os, git, sys
previous, current, branch = sys.argv[1:4]

WATCH_FILES = ('conf/python/requirements.txt',)

if branch:
    repository = git.Repo(os.getcwd())
    previous_commit = repository.commit(previous)
    current_commit = repository.commit(current)
    
    changed = []
    for diff in previous_commit.diff(current_commit).iter_change_type('M'):
        # This is hardly optimized, but I am le tired.
        for WATCH_FILE in WATCH_FILES:
            try:
                if diff.a_blob.path == WATCH_FILE or diff.b_blob.path == WATCH_FILE:
                    changed.append(WATCH_FILE)
            except:
                pass
    
    if changed:
        print "\nWARNING: The following watched files have changed!"
        for change in changed:
            print "  * %s" % change
        print ""