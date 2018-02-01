#!/usr/bin/python
#
# This is a rough Python script that demonstrates running AutoPkg with Jenkins
# as only a "check" action, using the ScriptTrigger plugin. It's assumed
# that AutoPkg is running directly out of a Git checkout from somewhere, but
# this is not necessary.
#
# Also note that the the '-d' option is given to hardcoded recipe
# search directories.
#
# It runs autopkg using --check and --report-plist, parses the resultant plist and
# triggers a build (by exiting zero) only if the 'new_downloads' array contains
# anything.
#
# This script assumes (with no error handling) three arguments:
# 1. The path to a Git checkout of AutoPkg
# 2. Path to a recipe list
# 3. Path to a directory to be used for overrides.

import plistlib
import os
import sys
import subprocess

from pprint import pprint
from shutil import rmtree
from tempfile import mkdtemp


work_dir = sys.argv[1]
recipe_list = sys.argv[2]
override_dir = sys.argv[3]

def runCommand(cmd, redirect_stdout=None):
    # overriding LC_CTYPE because without locale info, use of the tar command will fail
    # there's got to be a saner way of handling this,
    # at least getting at least the default locale types dynamically
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={'LC_CTYPE': 'en_CA.UTF-8'})
    out, err = p.communicate()
    if err:
        print >> sys.stderr, "Stderr output:"
        print >> sys.stderr, err
    return out


def main():
    auto_path = os.path.join(work_dir, 'Code/autopkg')
    # hardcoded additional recipe repos, for now..
    recipe_search_dirs = [os.path.join(os.getcwd(), 'autopkg-recipes'), os.path.join(os.getcwd(), 'keeleysam-recipes')]
    search_dirs_opts = []
    for search_dir in recipe_search_dirs:
        search_dirs_opts.extend(['-d', search_dir])
    report_cmd = [
    	auto_path,
        'run',
        '-c',
        '--report-plist',
        '--recipe-list', recipe_list,
        '--override-dir', override_dir
    ]
    report_cmd.extend(search_dirs_opts)

    # run it
    report_plist = runCommand(report_cmd)

    # clean up our temp workspace
    rmtree(work_dir)

    report = plistlib.readPlistFromString(report_plist)
    pprint(report)

	# trigger a build only if we got any new_downloads
    if len(report['new_downloads']) > 0:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()