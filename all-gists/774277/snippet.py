#!/usr/bin/env python -tt

"""Xcode4 installs and expects to find a git installation at /usr/bin.
This is a pain if you want to control your own installation of git that
might be installed elsewhere. This script replaces the git files in
/usr/bin with symlinks to the preferred installation.

Update the 'src_directory' to the location of your preferred git installation.
"""
import sys
import os

#- Configuration  -----------------------------------------------------------------
src_directory = '/usr/local/git/bin/' # preferred installation
#----------------------------------------------------------------------------------

dest_directory = '/usr/bin/'
files = ('git','git-cvsserver','git-receive-pack','git-shell','git-upload-archive','git-upload-pack','gitk')

def main():
    if os.getuid():
        print "This script needs to be run as 'sudo python update_git.py'"
        sys.exit(1)

    for a_file in files:
        src_file = os.path.join(src_directory, a_file)
        dest_file = os.path.join(dest_directory, a_file)

        if os.path.exists(dest_file):
            os.remove(dest_file)

        os.symlink(src_file, dest_file)

if __name__ == '__main__':
    main()
