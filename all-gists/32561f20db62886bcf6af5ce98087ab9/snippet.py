#!/usr/bin/env python2.7
# encoding=utf8
#
# Copyright 2007 Google Inc.
# Copyright 2016 Raphaël Doursenaud
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Tool for checking app.yaml skip-files regexes without deploying

Based on actual SDK code.
"""
import argparse
import logging
import os
import re

import yaml

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.WARNING)

parser = argparse.ArgumentParser(description="List skipped files according to app.yaml rules")
parser.add_argument("basepath", help="app.yaml path")
parser.add_argument("-r", "--reverse", help="Display *not* skipped files (aka uploaded files)", action="store_true")
args = parser.parse_args()


def file_iterator(base, skip_files, no_print=False, separator=os.path.sep):
    """Walks a directory tree, returning all the files. Follows symlinks.

    Args:
      base: The base path to search for files under.
      skip_files: A regular expression object for files/directories to skip.
      no_print: Don't print the skipped files and directories
      separator: Path separator used by the running system's platform.

    Yields:
      Paths of files found, relative to base.
    """
    dirs = ['']
    while dirs:
        current_dir = dirs.pop()
        entries = set(os.listdir(os.path.join(base, current_dir)))
        logger.debug(entries)
        for entry in sorted(entries):
            name = os.path.join(current_dir, entry)
            fullname = os.path.join(base, name)

            if separator == '\\':
                name = name.replace('\\', '/')

            if os.path.isfile(fullname):
                if skip_files.match(name):
                    logger.info('Ignoring file \'%s\': File matches ignore regex.', name)
                    if not no_print:
                        print name
                else:
                    yield name
            elif os.path.isdir(fullname):
                if skip_files.match(name):
                    logger.info('Ignoring directory \'%s\': Directory matches ignore regex.', name)
                    if not no_print:
                        print name
                else:
                    dirs.append(name)


def main():
    with open('app.yaml') as appyamlfile:
        appyaml = yaml.load(appyamlfile)
        logger.debug(appyaml)

    combined = '('
    for expression in appyaml['skip_files']:
        combined += expression + '|'
    combined = combined[:-1]
    combined += ')'
    logger.debug(combined)

    skip_files = re.compile(combined)

    files = file_iterator(args.basepath, skip_files, no_print=args.reverse)

    upload_files = list(files)
    if args.reverse:
        for name in upload_files:
            print name


if __name__ == '__main__':
    main()
