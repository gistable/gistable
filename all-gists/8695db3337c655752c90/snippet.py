#!/usr/bin/env python2.7

from __future__ import print_function
import sys
import os.path
import re
import shutil
from glob import glob
from HTMLParser import HTMLParser
from subprocess import check_output, check_call, Popen, CalledProcessError, PIPE
from pipes import quote

import requests

PATCHES_BASE_URL = 'http://algo.ing.unimo.it/people/paolo/disk_sched/patches/'
REQUIRED_BINARIES = ['rpm', 'wget', 'rpmbuild', 'spectool', 'patch', 'rpmdev-bumpspec']

def err(*args, **kwargs):
    kwargs['file'] = sys.stderr
    print(*args, **kwargs)

def check_binary(name):
    for path_dir in os.environ.get("PATH").split(os.pathsep):
        binary = os.path.join(path_dir, name)
        if os.path.isfile(binary) and os.access(binary, os.X_OK):
            return True

    err("Missing required binary '{0}'".format(name))
    sys.exit(1)

###

map(check_binary, REQUIRED_BINARIES)

if len(sys.argv) < 2:
    check_binary('yumdownloader')

    err('--- Retrieving RPM URL from yum')
    
    url_out = check_output(['yumdownloader', '--source', '--urls', 'kernel'])
    url_match = re.search(r'\S+\.src\.rpm', url_out)
    if not url_match:
        err("Error: failed to retrieve package URL")
        sys.exit(1)

    kernel_url = url_match.group(0)
    err(kernel_url)

    err("--- Downloading RPM")
    check_call(['wget', '-c', '-N', kernel_url])
    
    kernel_rpm = kernel_url.rsplit('/', 1)[1]
    kernel_rpm_path = os.path.join('.', kernel_rpm)
else:
    err('--- Using RPM from command line')

    kernel_url = None
    kernel_rpm_path = sys.argv[1]
    kernel_rpm = os.path.basename(kernel_rpm_path)
    if not kernel_rpm.endswith('.src.rpm'):
        err("Error: specified path does not have .src.rpm extension")
        sys.exit(1)

###

err('--- Verifying RPM')

check_call(['rpm', '-K', '--nosignature', kernel_rpm_path]) 

kernel_version = check_output(['rpm', '-qp', '--qf',  '%{VERSION}\n',
                               kernel_rpm_path]).strip()
kernel_major_version = kernel_version.rsplit('.', 1)[0]
err("Building kernel " + kernel_version)

###

err("--- Checking available patches")

patches_index = requests.get(PATCHES_BASE_URL).text

class PatchHTMLParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        HTMLParser.__init__(self, *args, **kwargs)

        self.patch_re = re.compile(r'^(\d+\.\d+)(?:\.\d+)*-v(\d+)r(\d+)/$')
        self.patches = {}

    def reset(self):
        HTMLParser.reset(self)

        self.patches = {}

    def handle_starttag(self, tag, attrs):
        if tag != 'a':
            return

        try:
            href = dict(attrs)['href']
        except KeyError:
            return

        match = self.patch_re.match(href)
        if match:
            major_version, patch_version, patch_rev = match.group(1, 2, 3)
            url = PATCHES_BASE_URL + '/' + match.group(0)

            self.patches.setdefault(major_version, [])
            self.patches[major_version].append((int(patch_version),
                                                int(patch_rev), url))

parser = PatchHTMLParser()
parser.feed(patches_index)

patch_versions = parser.patches
try:
    kernel_patch_versions = patch_versions[kernel_major_version]   
    patch_version, patch_rev, patch_url = max(kernel_patch_versions,
                                              key=lambda t: t[:2])
except KeyError:
    err('Failed to find patch for kernel version ' + kernel_major_version)
    sys.exit(1)
else:
    err("Using patch v{0}r{1} from '{2}'".format(patch_version, patch_rev,
                                                 patch_url))

###

err('--- Downloading patches')

patch_dest_dir = os.path.abspath(os.path.basename(patch_url.strip('/')))
if not os.path.isdir(patch_dest_dir):
    os.mkdir(patch_dest_dir)

check_call(['wget', '-nv', '-c', '-r', '-np', '-nd', '-e', 'robots=off',
            '--accept-regex', r'\.(BFQ|patch)$', patch_url],
            cwd=patch_dest_dir)

###

err('--- Creating build tree')

rpm_extract_dir = os.path.abspath(kernel_rpm[:-len('.src.rpm')])
if os.path.exists(rpm_extract_dir):
    err("Cleaning existing directory '{0}'".format(rpm_extract_dir))
    shutil.rmtree(rpm_extract_dir)

def build_dir(*args):
    return os.path.join(rpm_extract_dir, *args)

os.mkdir(rpm_extract_dir)
for d in ('BUILD', 'RPMS', 'SOURCES', 'SPECS', 'SRPMS'):
    os.mkdir(build_dir(d))

###

err('--- Extracting RPM')

check_call(['rpm', '-i', kernel_rpm_path, '-D', '%_topdir ' + build_dir()])

###

err('--- Downloading sources')

check_call(['spectool', '-gf', os.path.abspath(kernel_rpm_path),
           '-C', build_dir('SOURCES')])

###

err('--- Copying patches')

patch_files = []
for patch_file in glob(os.path.join(patch_dest_dir, '*.patch')):
    patch_name = os.path.basename(patch_file)
    err(patch_name)

    shutil.copy(patch_file, build_dir('SOURCES'))
    patch_files.append(patch_name)

if not patch_files:
    err("Error: no patches found!")
    sys.exit(1)

patch_files.sort()

###

err('--- Patching spec file')

def insert_patches(spec_fp, patch_files, patch_start=50000):
    def_re = re.compile(r'^# END OF PATCH DEFINITIONS')
    apply_re = re.compile(r'^# END OF PATCH APPLICATIONS')
    buildid_re = re.compile(r'^# % define buildid \.local')
    
    defined = False
    buildid_set = False

    for line in spec_fp:
        if not buildid_set and buildid_re.match(line):
            new_line = '%define buildid .bfq\n'
            buildid_set = True
            
            sys.stderr.write('+ ')
            sys.stderr.write(new_line)
            
            yield new_line
            continue

        if def_re.match(line):
            assert not defined
            for patch_num, patch in enumerate(patch_files, patch_start):
                new_line = 'Patch{0}: {1}\n'.format(patch_num, patch)

                sys.stderr.write('+ ')
                sys.stderr.write(new_line)
                yield new_line

            defined = True
        elif apply_re.match(line):
            assert defined
            for patch in patch_files:
                new_line = 'ApplyPatch {0}\n'.format(patch)
                
                sys.stderr.write('+ ')
                sys.stderr.write(new_line)
                yield new_line

        yield line

def apply_patch(original_path, patch_contents):
    proc = Popen(['patch', '-p0', original_path], stdin=PIPE)
    proc.communicate(input=patch_contents)
    proc.stdin.close()
    ret = proc.wait()
    if ret != 0:
        args = proc.args
        if not isinstance(args, basestring):
            args = ' '.join(args)

        raise CalledProcessError(ret, args, None)

spec_path = build_dir('SPECS', 'kernel.spec')
spec_orig_path = spec_path + '.orig'
shutil.copyfile(spec_path, spec_orig_path)

check_call(['rpmdev-bumpspec', '-c', 'Rebuild with BFQ support', spec_path])

# Fix failure to apply config-local to all archs, causing build erros
# (Red Hat bug 1160395)
apply_patch(spec_path, """
--- kernel.spec 2014-11-04 15:34:36.000000000 -0200
+++ kernel.spec 2014-11-04 15:35:41.608974427 -0200
@@ -1226,7 +1226,7 @@
 
 # Merge in any user-provided local config option changes
 %ifnarch %nobuildarches
-for i in %{all_arch_configs}
+for i in *.config
 do
   mv $i $i.tmp
   ./merge.pl %{SOURCE1000} $i.tmp > $i
""")

with open(spec_path, 'r') as fp:
    spec_contents = fp.readlines()

with open(spec_path, 'w') as fp:
    for line in insert_patches(spec_contents, patch_files):
        fp.write(line)

###

err('--- Patching kernel configuration')

with open(build_dir('SOURCES', 'config-local'), 'a') as fp:
    fp.write('\n')

    for cfg, val in (('CONFIG_IOSCHED_BFQ', 'y'),
                     ('CONFIG_CGROUP_BFQIO', 'y'),
                     ('CONFIG_DEFAULT_BFQ', 'y')):
        line = "{0}={1}\n".format(cfg, val)
        
        sys.stderr.write('+ ')
        sys.stderr.write(line)
        fp.write(line)

###

err('--- Building SRPM')

check_call(['rpmbuild', '-bs', '-D', '%_topdir ' + build_dir(''), spec_path])
