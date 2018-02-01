#!/usr/bin/python
#
# list_unused_munki_pkgs.py
# Tim Sutton
#
# Simple script to list all Munki pkgs not currently referenced in a specific list
# of catalogs.
# It does not delete anything.
#
# CATALOGS can be modified to a list of catalogs in your repo that should be indexed.
# PKGS_ROOT must also be defined to be root of the mounted 'pkgs' folder.
#
# This script needs to access your Munki repo as a client to retrieve catalog data, and
# therefore requires that all client tools are installed and a valid configuration exists
# for the ManagedInstalls domain. If there are additional secure preferences such as HTTP Basic
# Auth stored in /private/var/root, you would need to run this as root.

import os
import sys

sys.path.append('/usr/local/munki')
sys.path.append('/Applications/Utilities/Managed Software Update.app/Contents/Resources')
from munki import humanReadable
from munkilib import updatecheck

CATALOGS = ['testing', 'production']
PKGS_ROOT = '/Volumes/munki_repo/pkgs'

updatecheck.getCatalogs(CATALOGS)
defined_locations = []
for c in CATALOGS:
    for item in updatecheck.CATALOG[c]['items']:
        for path_key in ['installer_item_location', 'uninstaller_item_location']:
            if path_key in item.keys():
                report_item = {}
                report_item['path'] = os.path.join(PKGS_ROOT, item[path_key])
                report_item['size'] = item['installer_item_size']
                defined_locations.append(report_item)

totalbytes = 0
print "%-100s %-16s" % ("Path", "Size")
print

for r, d, f in os.walk(PKGS_ROOT):
    for phile in f:
        if (phile.endswith('.dmg') or phile.endswith('.pkg')) and \
            '.AppleDouble' not in r and \
            not phile.startswith('._'):
            repo_pkg_path = os.path.join(r, phile)
            relative_path = repo_pkg_path.split(PKGS_ROOT + '/')[1]
            if repo_pkg_path not in [k['path'] for k in defined_locations]:
                item_size = os.path.getsize(repo_pkg_path)
                print "%-100s %-16s" % (relative_path, humanReadable(item_size / 1024))
                totalbytes += item_size

print
print "Total size: %s" % (humanReadable(totalbytes / 1024))
