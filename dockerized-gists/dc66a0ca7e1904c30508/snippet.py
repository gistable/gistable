#!/usr/bin/env python
#
# Copyright (C) 2015 Alexander Taler
#
# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import filecmp
import glob
import json
import os
import shutil
import sys

DOCUMENTATION = '''
---
module: host local copy
short_description: Recursively copy files locally within the host
description:
    - Recursively copy files and directories locally on the host.  Supports
      Ansible C(--check) mode and change reporting by checking if files differ
      before copying them.
    - Links are copied as links. Things other than files, directories and links
      are not copied.
author: Alexander Taler
requirements:
    - Only works on UNIX hosts
version_added: null
options:
    src:
        description:
            - Host local file path or glob pattern naming the files which will
              be copied. If more than one item is matched then destination must
              be a directory. If nothing is matched, then nothing is copied.
        required: yes
        version_added: null
    dest:
        description:
            - Host local file path or name where the named files will be
              copied. If it ends with a / then it is a directory and source
              files will preserve their names, otherwise it specifies a new
              name and the source must be a single file or directory. Required
              parent directories will be created.
        required: yes
        version_added: null
    directory_mode:
        description:
            - The mode for directories which are copied, and missing parent
              directories which are created. If not specified system defaults
              are used.
        required: no
    fastcompare:
        description:
            - True to do file comparisons using modification time, false to
              compare contents. Default is true.
        required: no
extends_documentation_fragment:
    - files
'''

EXAMPLES = '''
# Copy the named file into a directory, preserving its name
- hostlocalcopy: src=/tmp/fund.conf dest=/etc
'''

# - Improvements to do
#   - Optional error on non-supported file type
#   - Verbose option to include list of changed files
#   - complete -not quick- file comparison
#   - handling permissions errors - see copy for example of x permission missing
#   - Optional removal of non-matching stuff from destination
#   - Behavior change if glob matches nothing
# - Improvements not to do:
#   - Not option to copy symlinks as files instead of links


# Test cases
#
# Files: (check expected behaviour and reported results)
#    Copy File
#    Copy Symlink
#    Copy Directory - recursively
#    Copy 3 levels of directory recursively
#    Not changed if File already exists
#    Not changed if Symlink already exists
#    Not changed if Directory already exists
#    Remove File in the way
#    Remove SYmlink in the way
#    Remove Directory in the way
#    Remove special stuff in the way (device, character special, ...)
#
# Invocation
#    Glob pattern matching
#    Copy to a directory preserving names (trailing /)
#    Copy to destination with new name (no trailing /)
#        * As file
#        * As symlink
#        * As directory
#    Creation of non-existing parent directory
#
# Error Scenarios:
#    wrong type of file in parent
#    lack of permission to create destination or parents
#    lack of permission to remove something in the way
#    glob matches multiple to new name
#    glob matchines nothing to new name


class HostLocalCopier:
    def __init__(self, module):
        self.module = module
        self.changed = False
        self.check_mode = module.check_mode

    def run(self):
        srcp = self.module.params['src']
        src = glob.iglob(os.path.expanduser(srcp))
        dest = os.path.expanduser(self.module.params['dest'])
        self.fastcompare = self.module.boolean(self.module.params["fastcompare"])

        self.load_common_file_args()

        # In the first operation mode, dest has a trailing separator, so files
        # matched by src preserve their names.
        if dest.endswith(os.sep):

            # Strip the trailing separator
            dest = dest[0:-len(os.sep)]

            # dest is the parent dir, so make sure it exists
            if self.create_parent_dirs(dest):
                # Copy each matched src to dest
                for srci in src:
                    desti = os.path.join(dest, os.path.basename(srci))
                    self.recursive_copy(srci, desti)

        # In the second operation mode, dest does not have a trailing separator,
        # and src must specify exactly one file.
        else:
            try:
                srci = src.next()
            except (StopIteration), e:
                self.module.fail_json(msg="No match for src: %s" % srcp)
            try:
                src.next()
                self.module.fail_json(msg="Too many matches for src: %s" % srcp)
            except (StopIteration), e:
                pass

            # Copy src to dest, creating parent directories if required
            if self.create_parent_dirs(os.path.dirname(dest)):
                self.recursive_copy(srci, dest)

        self.module.exit_json(changed=self.changed)


    def check_and_remove(self, dest):
        '''
        Check if changes should be made, and remove something at the
        destination. Return True if replacement should go ahead.
        '''
        self.changed = True
        if self.check_mode:
            return False

        # Clear whatever's in the way
        if os.path.isdir(dest):
            shutil.rmtree(dest)
        elif os.path.exists(dest):
            os.remove(dest)
        return True

    def recursive_copy(self, src, dest):
        # Recreate Links
        if os.path.islink(src):
            if os.path.islink(dest) and os.readlink(dest) == os.readlink(src):
                return # Already correct link
            elif self.check_and_remove(dest):
                os.symlink(os.readlink(src), dest)

        # Copy files
        elif os.path.isfile(src):
            # Remove anything in the way and copy the file if required
            if (not os.path.isfile(dest) or not filecmp.cmp(src, dest, self.fastcompare)):
                if self.check_and_remove(dest):
                    shutil.copy2(src, dest)
            # Ensure file attributes are correct
            self.set_attributes(dest, self.file_args)

        # Recursive directory copy
        elif os.path.isdir(src):
            if not os.path.isdir(dest):
                if self.check_and_remove(dest):
                    os.mkdir(dest)
            # Ensure directory attributes are correct
            self.set_attributes(dest, self.dir_args)

            # Recursive copy if destination exists
            if os.path.isdir(dest):
                for srce in os.listdir(src):
                    self.recursive_copy(os.path.join(src, srce),
                                        os.path.join(dest, srce))

        # Special files are ignored
        else:
            pass


    # TODO: This code is similar to a part of copy module from Ansible core
    # files modules, which can be found by the comment:
    #        Special handling for recursive copy - create intermediate dirs
    #
    # Recursively create parent directories to receive the copy.
    # Return false in check mode if the directory doesn't exist
    # Fail the module if the directory couldn't be created
    # Return True if the directory existed or was created
    def create_parent_dirs(self, pdir):
        # Check if directory already exists
        if (os.path.isdir(pdir)):
            return True
        # Check if something's in the way
        if (os.path.exists(pdir)):
            self.module.fail_json(msg="Parent is not a directory: %s" % pdir)
        # Create parents recursively
        if not self.create_parent_dirs(os.path.dirname(pdir)):
            return False
        # Create the directory
        self.changed = True
        if self.check_mode:
            return False
        os.mkdir(pdir)
        self.set_attributes(pdir, self.dir_args)
        return True


    # Load the common file args defined in the common file modules (ownership,
    # permissions, SELinux context)
    def load_common_file_args(self):
        self.file_args = self.module.load_file_common_arguments(self.module.params)
        self.dir_args = self.module.load_file_common_arguments(self.module.params)

        directory_mode = self.module.params["directory_mode"]
        if directory_mode is not None:
            self.dir_args['mode'] = directory_mode
        else:
            self.dir_args['mode'] = None


    # Set the attributes on the path
    def set_attributes(self, path, args):
        args['path'] = path
        if self.module.set_fs_attributes_if_different(args, False):
            self.changed = True


def main():
    module = AnsibleModule(
        argument_spec = dict(
            src              = dict(required=True),
            dest             = dict(required=True),
            directory_mode   = dict(required=False),
            fastcompare      = dict(required=False, default=True, choices=BOOLEANS),
        ),
        add_file_common_args=True,
        supports_check_mode=True,
    )

    hlcopier = HostLocalCopier(module)
    hlcopier.run()


from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
