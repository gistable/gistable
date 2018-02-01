#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013-2016 Vinay Sajip. License: MIT
#

import logging
import optparse     # for 2.6
import os
import re
import shutil
import subprocess
import sys
import tempfile

logger = logging.getLogger('wheeler')

from distlib.compat import configparser, filter
from distlib.database import DistributionPath, Distribution, make_graph
from distlib.locators import (JSONLocator, SimpleScrapingLocator,
                              AggregatingLocator, DependencyFinder)
from distlib.manifest import Manifest
from distlib.metadata import Metadata
from distlib.util import parse_requirement, get_package_data
from distlib.wheel import Wheel

EGG_INFO_RE = re.compile(r'(-py\d\.\d)?\.egg-info', re.I)

INSTALLED_DISTS = DistributionPath(include_egg=True)


def get_requirements(data):
    lines = []
    for line in data.splitlines():
        line = line.strip()
        if not line or line[0] == '#':
            continue
        lines.append(line)
    reqts = []
    extras = {}
    result = {'install': reqts, 'extras': extras}
    for line in lines:
        if line[0] != '[':
            reqts.append(line)
        else:
            i = line.find(']', 1)
            if i < 0:
                raise ValueError('unrecognised line: %r' % line)
            extra = line[1:i]
            extras[extra] = reqts = []
    return result


def convert_egg_info(libdir, prefix, options):
    files = os.listdir(libdir)
    ei = list(filter(lambda d: d.endswith('.egg-info'), files))[0]
    olddn = os.path.join(libdir, ei)
    di = EGG_INFO_RE.sub('.dist-info', ei)
    newdn = os.path.join(libdir, di)
    os.rename(olddn, newdn)
    if options.compatible:
        renames = {}
    else:
        renames = {
            'entry_points.txt': 'EXPORTS',
        }
    excludes = set([
        'SOURCES.txt',          # of no interest in/post WHEEL
        'installed-files.txt',  # replaced by RECORD, so not needed
        'requires.txt',         # added to METADATA, so not needed
        'PKG-INFO',             # replaced by METADATA
        'not-zip-safe',         # not applicable
    ])
    files = os.listdir(newdn)
    metadata = mdname = reqts = None
    for oldfn in files:
        pn = os.path.join(newdn, oldfn)
        if oldfn in renames:
            os.rename(pn, os.path.join(newdn, renames[oldfn]))
        else:
            if oldfn == 'requires.txt':
                with open(pn, 'r') as f:
                    reqts = get_requirements(f.read())
            elif oldfn == 'PKG-INFO':
                metadata = Metadata(path=pn)
                pd = get_package_data(metadata.name, metadata.version)
                metadata = Metadata(mapping=pd['index-metadata'])
                mdname = os.path.join(newdn, 'pydist.json')
            if oldfn in excludes or not options.compatible:
                os.remove(pn)
    if metadata:
        # Use Metadata 1.2 or later
        metadata.provides += ['%s (%s)' % (metadata.name,
                                           metadata.version)]
        # Update if not set up by get_package_data
        if reqts and not metadata.run_requires:
            metadata.dependencies = reqts
        metadata.write(path=mdname)
    manifest = Manifest(os.path.dirname(libdir))
    manifest.findall()
    paths = manifest.allfiles
    dp = DistributionPath([libdir])
    dist = next(dp.get_distributions())
    dist.write_installed_files(paths, prefix)


def install_dist(distname, workdir, options):
    pfx = '--install-option='
    purelib = pfx + '--install-purelib=%s/purelib' % workdir
    platlib = pfx + '--install-platlib=%s/platlib' % workdir
    headers = pfx + '--install-headers=%s/headers' % workdir
    scripts = pfx + '--install-scripts=%s/scripts' % workdir
    data = pfx + '--install-data=%s/data' % workdir
    # Use the pip adjacent to sys.executable, if any (for virtualenvs)
    d = os.path.dirname(sys.executable)
    files = filter(lambda o: o in ('pip', 'pip.exe'), os.listdir(d))
    if not files:
        prog = 'pip'
    else:
        prog = os.path.join(d, next(files))
    cmd = [prog, 'install',
           '--no-deps', '--quiet',
           '--index-url', 'https://pypi.python.org/simple/',
           '--timeout', '3', '--default-timeout', '3',
           purelib, platlib, headers, scripts, data, distname]
    result = {
        'scripts': os.path.join(workdir, 'scripts'),
        'headers': os.path.join(workdir, 'headers'),
        'data': os.path.join(workdir, 'data'),
    }
    print('Pipping %s ...' % distname)
    p = subprocess.Popen(cmd, shell=False, stdout=sys.stdout,
                         stderr=subprocess.STDOUT)
    stdout, _ = p.communicate()
    if p.returncode:
        raise ValueError('pip failed to install %s:\n%s' % (distname, stdout))
    for dn in ('purelib', 'platlib'):
        libdir = os.path.join(workdir, dn)
        if os.path.isdir(libdir):
            result[dn] = libdir
            break
    convert_egg_info(libdir, workdir, options)
    dp = DistributionPath([libdir])
    dist = next(dp.get_distributions())
    md = dist.metadata
    result['name'] = md.name
    result['version'] = md.version
    return result


def build_wheel(distname, options):
    result = None
    r = parse_requirement(distname)
    if not r:
        print('Invalid requirement: %r' % distname)
    else:
        dist = INSTALLED_DISTS.get_distribution(r.name)
        if dist:
            print('Can\'t build a wheel from already-installed '
                  'distribution %s' % dist.name_and_version)
        else:
            workdir = tempfile.mkdtemp()    # where the Wheel input files will live
            try:
                paths = install_dist(distname, workdir, options)
                paths['prefix'] = workdir
                wheel = Wheel()
                wheel.name = paths.pop('name')
                wheel.version = paths.pop('version')
                wheel.dirname = options.destdir
                wheel.build(paths)
                result = wheel
            finally:
                shutil.rmtree(workdir)
    return result


def main(args=None):
    parser = optparse.OptionParser(usage='%prog [options] requirement [requirement ...]')
    parser.add_option('-d', '--dest', dest='destdir', metavar='DESTDIR',
                      default=os.getcwd(), help='Where you want the wheels '
                      'to be put.')
    parser.add_option('-n', '--no-deps', dest='deps', default=True,
                      action='store_false',
                      help='Don\'t build dependent wheels.')
    options, args = parser.parse_args(args)
    options.compatible = True   # may add flag to turn off later
    if not args:
        parser.print_usage()
    else:
        # Check if pip is available; no point in continuing, otherwise
        try:
            with open(os.devnull, 'w') as f:
                p = subprocess.call(['pip', '--version'], stdout=f, stderr=subprocess.STDOUT)
        except Exception:
            p = 1
        if p:
            print('pip appears not to be available. Wheeler needs pip to '
                  'build  wheels.')
            return 1
        if options.deps:
            # collect all the requirements, including dependencies
            u = 'http://pypi.python.org/simple/'
            locator = AggregatingLocator(JSONLocator(),
                                         SimpleScrapingLocator(u, timeout=3.0),
                                         scheme='legacy')
            finder = DependencyFinder(locator)
            wanted = set()
            for arg in args:
                r = parse_requirement(arg)
                if not r.constraints:
                    dname = r.name
                else:
                    dname = '%s (%s)' % (r.name, ', '.join(r.constraints))
                print('Finding the dependencies of %s ...' % arg)
                dists, problems = finder.find(dname)
                if problems:
                    print('There were some problems resolving dependencies '
                          'for %r.' % arg)
                    for _, info in problems:
                        print('  Unsatisfied requirement %r' % info)
                wanted |= dists
            want_ordered = True     # set to False to skip ordering
            if not want_ordered:
                wanted = list(wanted)
            else:
                graph = make_graph(wanted, scheme=locator.scheme)
                slist, cycle = graph.topological_sort()
                if cycle:
                    # Now sort the remainder on dependency count.
                    cycle = sorted(cycle, reverse=True,
                                   key=lambda d: len(graph.reverse_list[d]))
                wanted = slist + cycle

                # get rid of any installed distributions from the list
                for w in list(wanted):
                    dist = INSTALLED_DISTS.get_distribution(w.name)
                    if dist or w.name in ('setuptools', 'distribute'):
                        wanted.remove(w)
                        s = w.name_and_version
                        print('Skipped already-installed distribution %s' % s)

            # converted wanted list to pip-style requirements
            args = ['%s==%s' % (dist.name, dist.version) for dist in wanted]

        # Now go build
        built = []
        for arg in args:
            wheel = build_wheel(arg, options)
            if wheel:
                built.append(wheel)
        if built:
            if options.destdir == os.getcwd():
                dest = ''
            else:
                dest = ' in %s' % options.destdir
            print('The following wheels were built%s:' % dest)
            for wheel in built:
                print('  %s' % wheel.filename)

if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)-8s %(name)s %(message)s',
                        filename='wheeler.log', filemode='w')
    try:
        rc = main()
    except Exception as e:
        print('Failed - sorry! Reason: %s\nPlease check the log.' % e)
        logger.exception('Failed.')
        rc = 1
    sys.exit(rc)
