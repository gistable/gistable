#!/usr/bin/python
#
# getosversionfromdmg.py
#
# Copyright (c) 2014 The Regents of the University of Michigan
#
# Retrieves the OS version and build from the InstallESD.dmg contained in
#    a typical "Install (Mac) OS X <Name>.app" bundle.
#
# To run:
# ./getosversionfromdmg.py \
#  "/Applications/Install OS X <Name>.app/Contents/SharedSupport/InstallESD.dmg"
#
# Two modes:
# - When run without sudo it reports the version and build to STDOUT
# - When run with sudo it reports the version and build to STDOUT and renames
#    the DMG to "InstallESD_<version>_<build>.dmg"
#
# Based on code written for the Munki project by Greg Neagle:
#   https://code.google.com/p/munki/

import os
import sys
import tempfile
import subprocess
import plistlib

def cleanUp():
    '''Cleanup our TMPDIR'''
    if TMPDIR:
        shutil.rmtree(TMPDIR, ignore_errors=True)

def fail(errmsg=''):
    '''Print any error message to stderr,
    clean up install data, and exit'''
    if errmsg:
        print >> sys.stderr, errmsg
    cleanUp()
    # exit
    exit(1)

def mountdmg(dmgpath, use_shadow=False):
    """
    Attempts to mount the dmg at dmgpath
    and returns a list of mountpoints
    If use_shadow is true, mount image with shadow file
    """
    mountpoints = []
    dmgname = os.path.basename(dmgpath)
    cmd = ['/usr/bin/hdiutil', 'attach', dmgpath,
                '-mountRandom', TMPDIR, '-nobrowse', '-plist',
                '-owners', 'on']
    if use_shadow:
        shadowname = dmgname + '.shadow'
        shadowroot = os.path.dirname(dmgpath)
        shadowpath = os.path.join(shadowroot, shadowname)
        cmd.extend(['-shadow', shadowpath])
    else:
        shadowpath = None
    proc = subprocess.Popen(cmd, bufsize=-1,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (pliststr, err) = proc.communicate()
    if proc.returncode:
        print >> sys.stderr, 'Error: "%s" while mounting %s.' % (err, dmgname)
    if pliststr:
        plist = plistlib.readPlistFromString(pliststr)
        for entity in plist['system-entities']:
            if 'mount-point' in entity:
                mountpoints.append(entity['mount-point'])

    return mountpoints, shadowpath

def unmountdmg(mountpoint):
    """
    Unmounts the dmg at mountpoint
    """
    proc = subprocess.Popen(['/usr/bin/hdiutil', 'detach', mountpoint],
                                bufsize=-1, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    (unused_output, err) = proc.communicate()
    if proc.returncode:
        print >> sys.stderr, 'Polite unmount failed: %s' % err
        print >> sys.stderr, 'Attempting to force unmount %s' % mountpoint
        # try forcing the unmount
        retcode = subprocess.call(['/usr/bin/hdiutil', 'detach', mountpoint,
                                '-force'])
        if retcode:
            print >> sys.stderr, 'Failed to unmount %s' % mountpoint

def getosversioninfo(mountpoint):
    """"getosversioninfo will attempt to retrieve the OS X version and build
        from the given mount point by reading /S/L/CS/SystemVersion.plist
        Most of the code comes from COSXIP without changes."""

    # Check for availability of BaseSystem.dmg
    basesystem_dmg = os.path.join(mountpoint, 'BaseSystem.dmg')
    if not os.path.isfile(basesystem_dmg):
        unmountdmg(mountpoint)
        fail('Missing BaseSystem.dmg in %s'% mountpoint)

    # Mount BaseSystem.dmg
    basesystemmountpoints, unused_shadowpath = mountdmg(basesystem_dmg)
    basesystemmountpoint = basesystemmountpoints[0]

    # Read SystemVersion.plist from the mounted BaseSystem.dmg
    system_version_plist = os.path.join(
        basesystemmountpoint,
        'System/Library/CoreServices/SystemVersion.plist')
    # Now parse the .plist file
    try:
        version_info = plistlib.readPlist(system_version_plist)

    # Got errors?
    except (ExpatError, IOError), err:
        unmountdmg(basesystemmountpoint)
        unmountdmg(mountpoint)
        fail('Could not read %s: %s' % (system_version_plist, err))

    # Done, unmount BaseSystem.dmg
    else:
        unmountdmg(basesystemmountpoint)

    # Return the version and build as found in the parsed plist
    return version_info.get('ProductUserVisibleVersion'), \
            version_info.get('ProductBuildVersion')

TMPDIR = None
def main():
    """Docstring"""
    global TMPDIR

    # Spin up a tmp dir for mounting
    TMPDIR = tempfile.mkdtemp(dir=TMPDIR)

    if len(sys.argv) < 2:
        print '\nNo path to an InstallESD.dmg provided, stopping.\nInvoke with "getosversionfromdmg.py <path to InstallESD.dmg>" and try again.\n'
        sys.exit(-1)

    dmg = sys.argv[1]
    dmgfilepath, ext = os.path.splitext(dmg)
    print 'Getting OS version and build for ' + dmg + "\n"
    mountpoints, shadow = mountdmg(dmg)
    for mount in mountpoints:
        if mount.find('dmg'):
            os_version, os_build = getosversioninfo(mount)
            print 'OS X Version: ' + os_version + '\n' + 'OS X Build: ' + os_build + '\n'
            unmountdmg(mount)
            if dmgfilepath.endswith('InstallESD') and os.getuid() == 0:
                print "We're running as root so we'll rename the DMG to reflect its OS version and build.\n"
                os.rename(dmg, dmgfilepath + '_' + os_version + '_' + os_build + '.dmg')
            elif not dmgfilepath.endswith('InstallESD') and os.getuid() == 0:
                print "Looks like the DMG file was previously renamed so we're skipping that step."
            else:
                print "Not running as root so we're not renaming " + dmg + " to contain the version and build."
                print "Re-run this tool with sudo to rename it.\n"

if __name__ == '__main__':
    main()
