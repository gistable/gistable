#! /usr/bin/env python
#  -*- coding: utf-8 -*-

#
# Nautilus Mass File Renamer is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author(s):        Thiago Bellini <hackedbellini@gmail.com>
#

"""Nautilus Mass File Renamer - v1.2

* How to install:
  - Copy this to ~/.gnome2/nautilus-scripts and give execution permission

* How to use:
  - Select the files you want to rename
  - The right button click will show this script under Scripts section
  - Select it and type a pattern
  - Wait for the script to finish

* TODO:
  - Present an option on zenity dialog to choose the separator
  - Preview changes before applying

"""

import os
import sys


TITLE = "Nautilus Mass File Renamer"
SEPARATOR = ' '
INVALID_CHARS = ('/',)


def _get_pattern():
    response = os.popen("zenity --entry --title %s --text 'Pattern:' "
                        "--width=320" % TITLE)
    pattern = response.read()
    pattern = pattern.split('\n')[0]

    if not pattern:
        raise ValueError("The pattern cannot be empty")

    # Look for invalid chars
    for invalid_char in INVALID_CHARS:
        if invalid_char in pattern:
            raise ValueError("The pattern cannot contain '%s' characteres"
                             % invalid_char)

    return pattern

def _get_new_name(old_name, pattern, suffix):
    new_name = "%s%s%s" % (pattern, SEPARATOR, suffix)

    if '.' in old_name:
        extension = old_name.split('.')[-1]
        new_name = "%s.%s" % (new_name, extension)

    return new_name

def main(files):
    if not files:
        return

    pattern = _get_pattern()
    suffix_number = 0
    # Will be used for to fill zeros before pattern
    len_suffix = len(str(len(files)))

    for file_ in files:
        old_file = os.path.split(file_)
        new_file = None

        while not new_file or (os.path.isfile(new_file) and file_ != new_file):
            suffix_number += 1
            new_name = _get_new_name(old_file[1], pattern,
                                     str(suffix_number).zfill(len_suffix))
            new_file = os.path.join(old_file[0], new_name)

        os.rename(file_, new_file)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

