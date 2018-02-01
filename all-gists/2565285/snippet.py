#!/usr/bin/env python

"""
Install a package from your local pip download cache without having to touch
the 'net at all.

You'll need to be using a pip download cache; that is, you'll need the
following in your ~/.pip/pip.cfg:

    [install]
    download-cache = /path/to/some/dir

And you'll need to have already installed the package(s) in question at
some time before your hotel's wifi went down.

But if you've done the above, then BEHOLD::

    $ pip-cache-install.py Django
    Found:
      (0) Django-1.2.4.tar.gz
      (1) Django-1.2.5.tar.gz
      (2) Django-1.3.1.tar.gz
      (3) Django-1.3.tar.gz
      (4) Django-1.4.tar.gz
      (5) Django-1.4-alpha-1.tar.gz

    Install which package? 4
    Unpacking ./.pip/dlcache/http%3A%2F%2Fpypi.python.org%2Fpackages%2Fsource%2FD%2FDjango%2FDjango-1.4.tar.gz
      Running setup.py egg_info for package from file:///Users/jacob/.pip/dlcache/http%253A%252F%252Fpypi.python.org%252Fpackages%252Fsource%252FD%252FDjango%252FDjango-1.4.tar.gz

    Installing collected packages: Django
      Running setup.py install for Django
        changing mode of build/scripts-2.7/django-admin.py from 644 to 755

        changing mode of /Users/jacob/.virtualenvs/yapc/bin/django-admin.py to 755
    Successfully installed Django
    Cleaning up...

Nifty, eh?
"""

import os
import sys
import glob
import ConfigParser

def main(argv):
    try:
        package_name = argv[1]
    except KeyError:
        print "Usage: %s package-name" % argv[0]
        return 1

    pipcfg = ConfigParser.ConfigParser()
    if not pipcfg.read(os.path.expanduser('~/.pip/pip.conf')):
        print "Failed to read ~/.pip/pip.conf."
        return 1

    try:
        dlcache = pipcfg.get('install', 'download-cache')
    except ConfigParser.Error:
        print "~/.pip/pip.conf have [install] download-cache defined."
        return 1

    matches = glob.glob1(dlcache, "*%s*.tar.gz" % package_name)
    if not matches:
        print "No match for %s." % package_name
        return 1

    if len(matches) == 1:
        return os.system('pip install %s' % os.path.join(dlcache, matches[0]))

    packages = [p.rsplit('%2F', 1)[1] for p in matches]
    print "Found:"
    for i, p in enumerate(packages):
        print "  (%s) %s" % (i, p)
    print
    install_index = None
    while not install_index:
        try:
            choice = int(raw_input("Install which package? "))
        except (ValueError, TypeError):
            continue
        if choice in range(len(packages)):
            install_index = choice

    return os.system('pip install %s' % os.path.join(dlcache, matches[install_index]))

if __name__ == '__main__':
    sys.exit(main(sys.argv))
