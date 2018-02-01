# Determine how many critical path packages failed to build from source using
# gcc -Werror=format-security. https://fedoraproject.org/wiki/Changes/FormatSecurity

import os
import subprocess

from collections import defaultdict
from fedora.client import PackageDB

pkgdb = PackageDB('https://admin.fedoraproject.org/pkgdb')
critpath = pkgdb.get_critpath_pkgs(['devel'])['devel']
print('%d critpath packages in devel' % len(critpath))

logs = 'http://people.fedoraproject.org/~halfie/rebuild-logs.txt'
if not os.path.exists('rebuild-logs.txt'):
    subprocess.call('wget %s' % logs, shell=True)

critpath_ftbfs = defaultdict(list)

with file('rebuild-logs.txt') as log:
    for line in log:
        pkg = '-'.join(line.split(':')[0].split('-')[:-2])
        if pkg in critpath:
            critpath_ftbfs[pkg].append(line.strip())

print('%d FTBFS with -Werror=format-security' % len(critpath_ftbfs))
for pkg in sorted(critpath_ftbfs):
    print('')
    for line in critpath_ftbfs[pkg]:
        print(line)