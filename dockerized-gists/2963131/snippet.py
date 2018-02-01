#!/usr/bin/python
"""
This is a prepare-commit-msg hook for use with Pivotal Tracker.

Copy this file to $GITREPOSITORY/.git/hooks/prepare-commit-msg
and mark it executable.

It will prepend [#<story id>] to your commit message.

See https://www.pivotaltracker.com/help/api?version=v3#scm_post_commit

Assumes you name your branches story-id/name.

For example: 12345678/my-cool-feature

This script can be found at https://gist.github.com/2963131

"""
import subprocess
import sys


def get_story():
    """Return the story id number associated with the current branch"""
    branchname = subprocess.check_output(["/usr/bin/git", "symbolic-ref", "HEAD"])
    # This looks like: refs/heads/12345678/my-cool-feature
    args = branchname.split('/')
    if len(args) != 4:
        raise ValueError("Branch name not in expected format")
    story = int(branchname.split('/')[2])
    return story


def prepend_commit_msg(text):
    """Prepend the commit message with `text`"""
    msgfile = sys.argv[1]

    with open(msgfile) as f:
        contents = f.read()

    with open(msgfile, 'w') as f:
        # Don't append if it's already there
        if not contents.startswith(text):
            f.write(text)
        f.write(contents)


def main():
    # Fail silently
    try:
        story = get_story()
        header = "[#%d] " % story
        prepend_commit_msg(header)
    except:
        pass

if __name__ == '__main__':
    main()
