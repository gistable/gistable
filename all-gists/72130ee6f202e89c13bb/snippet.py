#!/usr/bin/python
# #
# Copyright (c) 2014 by nexB, Inc. http://www.nexb.com/ - All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This script is a helper to select a requirement file based on some operating
system or architecture conditions. To use this script create a requirements
directory with a base.txt requirements file that contains common os-
independent requirements, and one requirement file for each OS/arch-specific
that contains at least this line at the top to always include the base
requirements::

  -r base.txt

To have a single pip command that uses the specific requirements file use this
in a shell script for posix OS::

  pip install -r $(select_requirements.py)

On windows, create a bat of cmd file that loads the windows-specific
requirements directly::

  for /f %%i in ('python select_requirements.py') do (set req_file="%%i")
  pip install -r %req_file%
"""

from __future__ import print_function

import os
import platform
import struct
import sys


# The code below is partially derived or inspired from
# https://github.com/kennethreitz/its.py and from code contributed to
# zc.buildout by nexB.
#
# Copyright (c) 2012, Kenneth Reitz All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer. Redistributions in binary
# form must reproduce the above copyright notice, this list of conditions and
# the following disclaimer in the documentation and/or other materials
# provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


# interpreter type
sys_version = sys.version.lower()
pypy = 'pypy' in sys_version
jython = 'java' in sys_version
ironpython = 'iron' in sys_version
# assume CPython, if nothing else.
cpython = not any((pypy, jython, ironpython,))


# major python major_python_versions as python2 and python3
major_python_versions = tuple(map(str, platform.python_version_tuple()))
python2 = major_python_versions[0] == '2'
python3 = major_python_versions[0] == '3'


# minor python major_python_versions as python24, python25 ... python36
minor_python_versions = ('24', '25', '26', '27',
                         '30', '31', '32', '33', '34', '35', '36')
for v in minor_python_versions:
    setattr(__builtins__, 'python' + v,
            ''.join(major_python_versions[:2]) == v)


# operating system
sys_platform = str(sys.platform).lower()
linux = 'linux' in sys_platform
windows = 'win32' in sys_platform
cygwin = 'cygwin' in sys_platform
solaris = 'sunos' in sys_platform
macosx = 'darwin' in sys_platform
posix = 'posix' in os.name.lower()


# bits and endianness
void_ptr_size = struct.calcsize('P') * 8
bits32 = void_ptr_size == 32
bits64 = void_ptr_size == 64
little_endian = sys.byteorder == 'little'
big_endian = sys.byteorder == 'big'


def select_requirements_file():
    """
    Print the path to a requirements file based on some os/arch condition.
    """
    if windows:
        print('requirements/win.txt')
    elif macosx:
        print('requirements/mac.txt')
    elif linux:
        print('requirements/linux.txt')
    elif cygwin:
        print('requirements/cygwin.txt')
    else:
        raise Exception('Unsupported OS/platform')


if __name__ == '__main__':
    select_requirements_file()
