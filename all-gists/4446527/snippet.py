#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
Written on 2013-01-03 by Philipp Klaus <philipp.l.klaus →AT→ web.de>.
Check <https://gist.github.com/4446527> for newer versions.
"""

import argparse, os, errno, re, shutil, sys, subprocess, glob
from datetime import datetime
from getpass import getpass

class SSHKeyError(Exception):
    pass
class NoKeyFile(SSHKeyError):
    pass
class TooManyKeyFiles(SSHKeyError):
    pass

def working_key(machine):
    """ Test, if we have a working ssh key set up """
    command = 'ssh -o BatchMode=yes root@%s "uname"' % machine
    try:
        subprocess.check_call(command, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False

def get_keyfile():
    """ Determine the public ssh key file on this system """
    keyfiles = glob.glob(os.path.expanduser('~/.ssh/id_[rd]sa.pub'))
    if len(keyfiles) == 0:
        raise NoKeyFile
    if len(keyfiles) > 1:
        raise TooManyKeyFiles
    return keyfiles[0]

def key_to(machine, keyfile):
    """ Add the public keyfile to the the remote machine.
        This is made specifically for OpenWrt.
        http://wiki.openwrt.org/doku.php?id=oldwiki:dropbearpublickeyauthenticationhowto
    """
    if working_key(machine):
        return
    pubkey = file(keyfile).read().replace('\n', ' ')
    command = 'ssh root@%s "echo %s >> /etc/dropbear/authorized_keys; chmod 0600 /etc/dropbear/authorized_keys"' % (machine, pubkey)
    subprocess.call(command, shell=True)

def backup(host, folder='./'):
    """ Backup the settings from the router to folder """
    folder = os.path.join(folder, host)
    try:
        os.makedirs(folder)
    except OSError, e:
        if not e.errno == errno.EEXIST:
            raise
    when = datetime.now().replace(microsecond = 0)
    whenstring = when.isoformat().replace('T', '_').replace(':', '-')
    # Backup the list of installed packages
    script = 'ssh root@%s "opkg list-installed"' % (host,)
    packagelist = subprocess.check_output(script, shell=True)
    packagelist_file = open(os.path.join(folder, 'packagelist_%s.txt' % whenstring), 'w')
    packagelist_file.write(packagelist)
    packagelist_file.close()
    # Create an archive of the /etc folder on the remote host
    filename = '/tmp/etc-backup_%s.tar.gz' % whenstring
    script = 'ssh root@%s "tar -zcvf %s /etc"' % (host, filename)
    subprocess.call(script, shell=True)
    print "Created the backup file on the remote host."
    # Move the file to the local host
    print "Moving the archived configuration file to %s now." % folder
    script = 'scp root@%s:%s %s' % (host, filename, folder)
    subprocess.call(script, shell=True)
    print "Finished Moving the backup file %s to %s." % (filename, folder)
    print "It contains the files from the configuration folder /etc on the machine %s." % host
    # Remove the archive from the device
    print "Now removing the archive file on the device"
    script = 'ssh root@%s "rm %s"' % (host, filename)
    subprocess.call(script, shell=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Backing up the /etc directory of remote computers.')
    parser.add_argument('machines', metavar='machine', nargs='+',
                        help='the machines to get a backup of /etc from')
    #parser.add_argument('-q', '--quiet', action='store_true',
    #                    help='Silence the less important output of this tool.')
    parser.add_argument('-k', '--keys', action='store_true',
                        help='Add your SSH keys to the authorized keys on the remote machines first.')
    parser.add_argument('-f', '--folder', default='./',
                        help='Folder to store the /etc backups.')
    args = parser.parse_args()

    if args.keys:
        keyfile = get_keyfile()
        for machine in args.machines:
            print "Fixing key on %s" % machine
            key_to(machine, keyfile)

    for machine in args.machines:
        print "Backing up %s" % machine
        backup(machine, args.folder)