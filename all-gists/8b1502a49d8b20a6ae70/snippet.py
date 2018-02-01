#!/usr/bin/env python
#coding=utf-8

import apt
import apt_pkg
from time import strftime
import os
import subprocess
import sys


"""
Following functions are used to return package info of available updates.
See: /usr/lib/update-notifier/apt_check.py
"""
SYNAPTIC_PINFILE = "/var/lib/synaptic/preferences"
DISTRO = subprocess.check_output(["lsb_release", "-c", "-s"],
                                 universal_newlines=True).strip()


def clean(cache,depcache):
    """ unmark (clean) all changes from the given depcache """
    # mvo: looping is too inefficient with the new auto-mark code
    # for pkg in cache.Packages:
    #    depcache.MarkKeep(pkg)
    depcache.init()


def saveDistUpgrade(cache,depcache):
    """ this functions mimics a upgrade but will never remove anything """
    depcache.upgrade(True)
    if depcache.del_count > 0:
        clean(cache,depcache)
    depcache.upgrade()


def get_update_packages():
    """
    Return a list of dict about package updates
    """
    pkgs = []

    apt_pkg.init()
    # force apt to build its caches in memory for now to make sure
    # that there is no race when the pkgcache file gets re-generated
    apt_pkg.config.set("Dir::Cache::pkgcache","")

    try:
        cache = apt_pkg.Cache(apt.progress.base.OpProgress())
    except SystemError as e:
        sys.stderr.write("Error: Opening the cache (%s)" % e)
        sys.exit(-1)

    depcache = apt_pkg.DepCache(cache)
    # read the pin files
    depcache.read_pinfile()
    # read the synaptic pins too
    if os.path.exists(SYNAPTIC_PINFILE):
        depcache.read_pinfile(SYNAPTIC_PINFILE)
    # init the depcache
    depcache.init()

    try:
        saveDistUpgrade(cache,depcache)
    except SystemError as e:
        sys.stderr.write("Error: Marking the upgrade (%s)" % e)
        sys.exit(-1)

    # use assignment here since apt.Cache() doesn't provide a __exit__ method
    # on Ubuntu 12.04 it looks like
    # aptcache = apt.Cache()
    for pkg in cache.packages:
        if not (depcache.marked_install(pkg) or depcache.marked_upgrade(pkg)):
            continue
        inst_ver = pkg.current_ver
        cand_ver = depcache.get_candidate_ver(pkg)
        if cand_ver == inst_ver:
            continue
        record = {"name": pkg.name,
                  "security": isSecurityUpgrade(pkg, depcache),
                  "section": pkg.section,
                  "current_version": inst_ver.ver_str if inst_ver else '-',
                  "candidate_version": cand_ver.ver_str  if cand_ver else '-',
                  "priority": cand_ver.priority_str}
        pkgs.append(record)

    return pkgs


def isSecurityUpgrade(pkg, depcache):

    def isSecurityUpgrade_helper(ver):
        """ check if the given version is a security update (or masks one) """
        security_pockets = [("Ubuntu", "%s-security" % DISTRO),
                            ("gNewSense", "%s-security" % DISTRO),
                            ("Debian", "%s-updates" % DISTRO)]

        for (file, index) in ver.file_list:
            for origin, archive in security_pockets:
                if (file.archive == archive and file.origin == origin):
                    return True
        return False
    inst_ver = pkg.current_ver
    cand_ver = depcache.get_candidate_ver(pkg)

    if isSecurityUpgrade_helper(cand_ver):
        return True

    # now check for security updates that are masked by a
    # canidate version from another repo (-proposed or -updates)
    for ver in pkg.version_list:
        if (inst_ver and
            apt_pkg.version_compare(ver.ver_str, inst_ver.ver_str) <= 0):
            #print "skipping '%s' " % ver.VerStr
            continue
        if isSecurityUpgrade_helper(ver):
            return True

    return False


def print_result(pkgs):
    """
    Print package updates in a table
    """
    security_updates = filter(lambda x: x.get('security'), pkgs)
    text = list()
    text.append('Check Time: %s' % strftime('%m/%d/%Y %H:%M:%S'))
    if not pkgs:
        text.append('No available updates on this machine.')
    else:
        # Updates are available, build a table
        text.append('%d packages can be updated.' % len(pkgs))
        text.append('%d updates are security updates.' % len(security_updates))
        text.append('-' * 100)
        # List available security updates
        text.append('Package Name'.ljust(30) +
                    'Current Version'.ljust(30) +
                    'Latest Version'.ljust(30) +
                    'Security'.ljust(10))
        text.append('-' * 100)
        for pkg in pkgs:
            text.append('{:<30}{:<30}{:<30}{:<10}'.format(pkg.get('name'),
                pkg.get('current_version'),
                pkg.get('candidate_version'),
                '*' if pkg.get('security') else ''))
    text.append('=' * 100)
    return '\n'.join(text)

if __name__ == '__main__':
    pkgs = get_update_packages()
    print print_result(pkgs)
