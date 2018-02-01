#!/usr/bin/env python
"""
Use pip to get a list of local packages to check against one or more package
indexes for updated versions.
"""
import pip
import sys, xmlrpclib
from cStringIO import StringIO
from distutils.version import StrictVersion, LooseVersion

def get_local_packages():
    """
    Call pip's freeze -l
    
    returns a list of package_name, version tuples
    """
    sys.stdout = mystdout = StringIO()
    pip.main(['freeze', '-l'])
    sys.stdout = sys.__stdout__
    
    pkgs = mystdout.getvalue().split('\n')
    return [p.split('==') for p in pkgs]

def find_current_version(package, index_urls=None):
    """
    Using the XMLRPC method available for PyPI, get the most recent version
    of <package> from each of the index_urls and figure out which one (if any)
    is higher
    
    Returns a tuple of the index with the higher version and the version it has
    """
    if index_urls is None:
        index_urls = ['http://pypi.python.org/pypi',]
    cur_version = '0'
    cur_index = ''
    for index_url in index_urls:
        pypi = xmlrpclib.ServerProxy(index_url, xmlrpclib.Transport())
        pypi_hits = pypi.package_releases(package)
        if len(pypi_hits) > 0:
            if compare_versions(pypi_hits[0], cur_version) == 1:
                cur_version = pypi_hits[0]
                cur_index = index_url
    
    return cur_index, cur_version

def compare_versions(version1, version2):
    """
    Compare 2 versions, starting with StrictVersion, and falling back on
    LooseVersion
    """
    try:
        return cmp(StrictVersion(version1), StrictVersion(version2))
    # in case of abnormal version number, fall back to LooseVersion
    except ValueError:
        return cmp(LooseVersion(version1), LooseVersion(version2))

def output_line(pkg_name, new_version, old_version, index_url):
    """
    Output the line showing the formatted information
    """
    msg = "%(bd)s%(pkg_name)s%(nm)s (%(new)s) via %(index)s. Currently %(old)s."
    params = {
        'bd': BOLD,
        'nm': NORMAL,
        'pkg_name': pkg_name,
        'new': new_version,
        'old': old_version,
        'index': index_url,
    }
    print msg % params

NEWER = lambda x,y: compare_versions(str(x), y) == 1

if __name__ == '__main__':
    import curses
    curses.setupterm()
    CLEAR_SCREEN = curses.tigetstr('clear')
    BOLD = curses.tigetstr("bold")
    NORMAL = curses.tigetstr('sgr0')
    
    if len(sys.argv) > 1:
        indexes = sys.argv[1:]
    else:
        indexes = ['http://pypi.python.org/pypi',]
    print CLEAR_SCREEN + BOLD + "Packages with newer versions:" + NORMAL
    print ""
    
    for pkg in get_local_packages():
        # pip outputs a single 0 at the end of the list. Ignore it.
        if len(pkg) < 2:
            continue
        
        index, current_version = find_current_version(pkg[0], index_urls=indexes)
        if current_version and NEWER(str(current_version), pkg[1]):
            output_line(pkg[0], current_version, pkg[1], index)
