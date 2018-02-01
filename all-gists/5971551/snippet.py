#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ft=python ts=4 sw=4 expandtab
#
# Copyright (c) 2013 Reed Kraft-Murphy <reed@reedmurphy.net>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import print_function

__version__ = "0.0.4"

import argparse
import datetime
import fcntl
import os
import os.path
import shutil
import sys
import tempfile


class FileRotator:
    date_formats = {
            'hourly': '%Y-%m-%dT%H',
            'daily': '%Y-%m-%d',
            'weekly': '%Y-W%W',
            'monthly': '%Y-%m',
    }
    def __init__(self, dest_dir, hours, days, weeks, months, hard_link=False,
            remove=False, verbose=False):
        self.keep_count = {
                'hourly': hours,
                'daily': days,
                'weekly': weeks,
                'monthly': months,
        }

        self.dest_dir = dest_dir
        self.hard_link = hard_link
        self.remove = remove
        self.verbose = verbose

        self.files = []

    def add_files(self, files):
        self.files.extend(files)

    def __verb(self, msg):
        if self.verbose:
            print(msg)

    @staticmethod
    def copy(src, dest):
        shutil.copy2(src, dest)
        stat = os.stat(src)
        os.chown(dest, stat.st_uid, stat.st_gid)

    def __rotate_file(self, filename, dry_run=False):
        basename = os.path.basename(filename)

        temp_file = os.path.join(self.__temp_dir, basename)
        self.__verb("Copying {} to {}".format(basename, temp_file))
        if not dry_run:
            self.copy(filename, temp_file)

        for rotate_class, prefix_format in self.date_formats.iteritems():
            keep_count = self.keep_count[rotate_class]
            dir_path = os.path.join(self.dest_dir, rotate_class,
                    datetime.datetime.now().strftime(prefix_format))
            dest_path = os.path.join(dir_path, basename)

            if keep_count > 0 and not os.path.isdir(dir_path):
                self.__verb("mkdir {}".format(dir_path))
                if not dry_run:
                    os.mkdir(dir_path)

            if keep_count <= 0:
                self.__verb("{} limit {}, not creating file {}".format(
                    rotate_class, keep_count, dest_path))
            elif os.path.exists(dest_path):
                self.__verb("{} exists, skipping".format(dest_path))
            else:
                if self.hard_link:
                    self.__verb("Linking {}".format(dest_path))
                    if not dry_run:
                        os.link(temp_file, dest_path)
                else:
                    self.__verb("Copying {}".format(dest_path))
                    if not dry_run:
                        self.copy(temp_file, dest_path)

        if self.hard_link:
            self.__verb("Unlinking {}".format(temp_file))
            if not dry_run:
                os.unlink(temp_file)

        if self.remove:
            self.__verb("Removing source {}".format(filename))
            if not dry_run:
                os.unlink(filename)

    def __trim(self, dry_run=False):
        for rotate_class, keep_count in self.keep_count.iteritems():
            dir_path = os.path.join(self.dest_dir, rotate_class)
            if not os.path.exists(dir_path):
                existing_count = 0
                existing = []
            else:
                existing = sorted(os.listdir(dir_path))
                existing_count = len(existing)

            self.__verb("{}/{} {} directories".format(
                existing_count, keep_count, rotate_class))
            if existing_count > keep_count:
                self.__verb("Trimming to {}".format(keep_count))
                for directory in existing[:-keep_count]:
                    directory = os.path.join(dir_path, directory)
                    self.__verb("Removing {}".format(directory))
                    if not dry_run:
                        shutil.rmtree(directory)

    def rotate(self, dry_run=False):
        result = os.EX_OK
        if dry_run:
            print("Performing a dry run - no changes will be made.")

        if not os.path.isdir(self.dest_dir):
            self.__verb("mkdir -p {}".format(self.dest_dir))
            if not dry_run:
                os.makedirs(self.dest_dir)

        for rotate_class, count in self.keep_count.iteritems():
            if count > 0:
                dir_path = os.path.join(self.dest_dir, rotate_class)
                if not os.path.isdir(dir_path):
                    self.__verb("mkdir {}".format(dir_path))
                    if not dry_run:
                        os.mkdir("{}".format(dir_path))

        if dry_run:
            self.__temp_dir = "/tmp"
        else:
            self.__temp_dir = tempfile.mkdtemp()
        self.__verb("Working directory {}".format(self.__temp_dir))

        for in_file in self.files:
            file_path = os.path.abspath(in_file.name)
            self.__verb("rotating {}".format(file_path))
            self.__rotate_file(file_path, dry_run)

        self.__trim(dry_run)

        if not dry_run:
            self.__verb("Removing working directory {}".format(self.__temp_dir))
            shutil.rmtree(self.__temp_dir)

        return result

class ConfigFileArgumentParser(argparse.ArgumentParser):
    def convert_arg_line_to_args(self, arg_line):
        for arg in arg_line.split():
            if not arg.strip():
                continue
            yield arg

if __name__ == "__main__":
    CONFIG_FILES = [
            '/etc/rotate',
            '~/.rotate',
            './.rotate',
    ]

    parser = ConfigFileArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument(
            '-v', '--verbose',
            help="be more verbose",
            action='store_true')
    parser.add_argument(
            '-V', '--version',
            help="display version information and exit",
            action='store_true')
    parser.add_argument(
            '-H', '--hours',
            help="number of hourly versions to keep",
            default=0,
            type=int)
    parser.add_argument(
            '-d', '--days',
            help="number of daily versions to keep",
            default=0,
            type=int)
    parser.add_argument(
            '-w', '--weeks',
            help="number of weekly versions to keep",
            default=0,
            type=int)
    parser.add_argument(
            '-m', '--months',
            help="number of monthly versions to keep",
            default=0,
            type=int)

    parser.add_argument(
            '-n', '--dry-run',
            help="dry run - do not make any changes",
            action='store_true')
    parser.add_argument(
            '-l', '--hard-link',
            help="hard link duplicate files to save space",
            action='store_true')
    parser.add_argument(
            '-r', '--remove',
            help="remove original files",
            action='store_true')

    parser.add_argument(
            'directory',
            help="destination directory",
            nargs='?')
    parser.add_argument(
            'file',
            help="files to rotate",
            type=argparse.FileType('r'),
            nargs='*')

    parser.epilog = """%(prog)s will attempt to read configuration directives
    from the following files, with each subsequent file overriding directives,
    and command-line flags overriding them again:
    {}""".format(', '.join(
        "`{}`".format(filename) for filename in CONFIG_FILES))

    arg_files = ['@' + os.path.abspath(os.path.expanduser(filename))
            for filename in CONFIG_FILES
            if os.path.exists(filename)]
    arguments = parser.parse_args(arg_files + sys.argv[1:])

    exit_code = os.EX_SOFTWARE
    if arguments.version:
        print("{program} {version}".format(
            program=os.path.basename(__file__),
            version=__version__))
        exit_code = os.EX_OK
    elif not arguments.directory:
        print("You must supply a destination directory", file=sys.stderr)
        parser.print_usage(sys.stderr)
    elif not arguments.file:
        print("You must supply one of more files to rotate", file=sys.stderr)
        parser.print_usage(sys.stderr)
    elif not any(
            getattr(arguments, x)
            for x in ['hours', 'days', 'weeks', 'months']):
        print("You must supply at least one of "
                + "--hours / --days / --weeks / --months\n",
                file=sys.stderr)
        parser.print_usage(sys.stderr)
    else:
        try:
            fr = FileRotator(arguments.directory, hours=arguments.hours,
                    days=arguments.days, weeks=arguments.weeks,
                    months=arguments.months, verbose=arguments.verbose,
                    hard_link=arguments.hard_link, remove=arguments.remove)
            fr.add_files(arguments.file)
            exit_code = fr.rotate(dry_run=arguments.dry_run)
        except KeyboardInterrupt:
            exit_code = os.EX_OK
        except IOError as ioe:
            if ioe.errno == 32:  # Broken pipe
                exit_code = os.EX_OK
            else:
                raise
    sys.exit(exit_code)