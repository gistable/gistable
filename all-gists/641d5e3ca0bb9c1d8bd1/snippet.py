#!/usr/bin/python

# gpgedit lets you edit a gpg-encrypted file without much fuzz -- similar to
# sudoedit.
#
# For this to achieve, gpgedit uses gpg to decrypt your file and save the
# plain text in a temporary file under /dev/shm (tmpfs) which will open in
# an editor. After the changes have been saved and the editor closed your
# plain text will be encrypted and written to the original file.
#
# The following environment variables (in this order) will be searched for an
# editor:
#   GPG_EDITOR, VISUAL and EDITOR
# The default editor is 'nano'.
#
# Thanks to Luke from StackOverflow for his answer at
#   http://stackoverflow.com/a/12289967/346095
# I took some inspiration from his script.

# Copyright © 2014 Arne Ludwig <arne.ludwig@posteo.de>
#
# gpgedit is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# gpgedit is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# gpgedit. If not, see <http://www.gnu.org/licenses/>.


from __future__ import print_function
from sys import version_info
if version_info < (2, 6):
    raise "gpgedit: must use python 2.6 or greater"

import contextlib
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
    

def show_usage():
    """Show usage information
    """
    print('USAGE gpgedit [GPGOPTS] [--symmetric|-c|--encrypt|-e] [--new] [--] FILE', file=sys.stderr)

def get_input_filename():
    """Get filename to decrypt and edit

    Exits if no file is found.
    """
    filename = None
    for arg in sys.argv:
        if arg == '--':
            continue
            filename = arg

    if filename == None:
        if(len(sys.argv) > 0):
            if not sys.argv[-1].startswith('-'):
                filename = sys.argv[-1]
        if filename == None:
            show_usage()
            raise Exception('missing argument FILE')
    return filename

def get_editor_command():
    """Get editor command

    Try environment variable GPG_EDITOR, VISUAL and EDITOR in that
    order; otherwise use the default value 'nano'
    """
    editor = None
    for varName in ['GPG_EDITOR', 'VISUAL', 'EDITOR']:
        if editor == None:
            editor = os.environ.get(varName)
    if editor == None:
        editor = 'nano'
    return re.split(r'(?<!\\) ', editor)

def stat_has_changed(stat_before, stat_after):
    for attr in ['st_mode', 'st_ino', 'st_dev', 'st_nlink', 'st_uid', 'st_gid',
                 'st_size', 'st_mtime', 'st_ctime']:
        if getattr(stat_before, attr) != getattr(stat_after, attr):
            return True
    return False

def decrypt(cipherfile, plainfile, opts):
    """Decrypt cipherfile using gpg and write the result to plainfile
    """
    cmd = ['gpg'] + list(opts) + ['--yes', '--decrypt', '--output' , plainfile, '--', cipherfile]
    exit_code = subprocess.call(cmd)
    if exit_code != 0:
        raise Exception("gpg exited with status {}".format(exit_code))

def encrypt(plainfile, cipherfile, opts):
    """Encrypt plainfile using gpg and write the result to cipherfile
    """
    cmd = ['gpg'] + list(opts) + ['--yes', '--output' , cipherfile, '--', plainfile]
    exit_code = subprocess.call(cmd)
    if exit_code != 0:
        raise Exception("gpg exited with status {}".format(exit_code))

def edit(filename):
    """Edit the file with an editor
    """
    editor = get_editor_command()
    cmd = editor + [filename]
    exit_code = subprocess.call(cmd)
    if exit_code != 0:
        raise Exception("{} exited with status {}".format(editor, exit_code))

def get_keyid(filename):
    cmd = ['gpg', '--list-packets', '--list-only', '--', filename]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    rawout = proc.communicate()[0];
    match = re.search(r"keyid ([A-F0-9]+)", rawout)
    if match == None or proc.returncode != 0:
        return None
    else:
        return match.group(1)

@contextlib.contextmanager
def backup(filename, backupext='~'):
    backup = filename + backupext
    shutil.copy(filename, backup)

    before = os.stat(backup)
    try:
        yield backup
    except:
        after = os.stat(backup)
        if not stat_has_changed(before, after):
            shutil.copyfile(backup, filename)
        raise
    finally:
        os.remove(backup)

ENCRYPT_OPTS = frozenset(['-e', '--encrypt', '-c', '--symmetric'])
def decrypt_opts(opts):
    newopts = list(opts)
    for opt in ENCRYPT_OPTS | frozenset(['--new']):
        if opt in opts:
            newopts.remove(opt)
    return newopts

NO_RECIPIENT_OPTS = frozenset(['-c', '--symmetric', '-r', '--recipient'])
def encrypt_opts(filename, opts):
    newopts = list(opts)
    opts = frozenset(opts)
    if '--new' in opts:
        newopts.remove('--new')

    if opts.isdisjoint(ENCRYPT_OPTS):
        newopts.append('--encrypt')

    if opts.isdisjoint(NO_RECIPIENT_OPTS):
        keyid = get_keyid(filename)
        if keyid != None:
            newopts += ['--recipient', keyid]
        else:
            print('gpgedit: warning: could not determine keyid')
    return newopts

@contextlib.contextmanager
def decrypted_file(filename, opts):
    with backup(filename, '-gpgedit~'):
        with tempfile.NamedTemporaryFile(mode='rw+', prefix='gpgedit-', dir='/dev/shm') as tmpfile:
            if '--new' not in opts:
                decrypt(filename, tmpfile.name, decrypt_opts(opts))

            before = os.stat(tmpfile.name)
            yield tmpfile
            after = os.stat(tmpfile.name)

            if not stat_has_changed(before, after):
                print("gpgedit: file unchanged; not writing encrypted file.")
            else:
                encrypt(tmpfile.name, filename, encrypt_opts(filename, opts))

def gpgedit():
    cipherfile = get_input_filename()
    ndrop = 1
    if len(sys.argv) >= 2 and sys.argv[-2] == '--':
        ndrop += 1
    # Drop the script name and filename-related parts.
    opts = sys.argv[1:-ndrop]
    if '--new' in opts:
        # Create empty file.
        open(cipherfile, 'a').close()
    with decrypted_file(cipherfile, opts) as plainfile:
        edit(plainfile.name)

if __name__ == '__main__':
    if '--usage' in sys.argv or '--help' in sys.argv or '-h' in sys.argv:
        show_usage()
    else:
        try:
            gpgedit()
        except Exception as e:
            print("gpgedit: {}".format(e), file=sys.stderr)
