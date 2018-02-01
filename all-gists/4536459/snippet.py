#! /usr/bin/env python
# License: http://creativecommons.org/publicdomain/zero/1.0/
# See http://preshing.com/20130115/view-your-filesystem-history-using-python
import optparse
import os
import fnmatch
import time

# Parse options
parser = optparse.OptionParser(usage='Usage: %prog [options] path [path2 ...]')
parser.add_option('-g', action='store', type='long', dest='secs', default=10,
                  help='set threshold for grouping files')
parser.add_option('-f', action='append', type='string', dest='exc_files', default=[],
                  help='exclude files matching a wildcard pattern')
parser.add_option('-d', action='append', type='string', dest='exc_dirs', default=[],
                  help='exclude directories matching a wildcard pattern')
options, roots = parser.parse_args()

if len(roots) == 0:
    print('You must specify at least one path.\n')
    parser.print_help()

def iterFiles(options, roots):
    """ A generator to enumerate the contents directories recursively. """
    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root):
            name = os.path.split(dirpath)[1]
            if any(fnmatch.fnmatch(name, w) for w in options.exc_dirs):
                del dirnames[:]  # Don't recurse here
                continue
            stat = os.stat(os.path.normpath(dirpath))
            yield stat.st_mtime, '', dirpath  # Yield directory
            for fn in filenames:
                if any(fnmatch.fnmatch(fn, w) for w in options.exc_files):
                    continue
                path = os.path.join(dirpath, fn)
                stat = os.lstat(os.path.normpath(path))  # lstat fails on some files without normpath
                mtime = max(stat.st_mtime, stat.st_ctime)
                yield mtime, stat.st_size, path  # Yield file

# Build file list, sort it and dump output
ptime = 0
for mtime, size, path in sorted(iterFiles(options, roots), reverse=True):
    if ptime - mtime >= options.secs:
        print('-' * 30)
    timeStr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
    print('%s %10s %s' % (timeStr, size, path))
    ptime = mtime
