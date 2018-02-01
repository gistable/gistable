#!/usr/bin/python -tt
# (c) 2012, Stefan Midjich
# Written by Stefan Midjich <swehack@gmail.com>
#
# This module was written for Ansible.
# It doesn't support all of Homebrew yet. 
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

try: 
	import json
except ImportError:
	import simplejson as json
import os
import sys
import shlex
import subprocess
import syslog
import traceback
import warnings

BREW = '/usr/local/bin/brew'

def exit_json(rc=0, **kwargs):
	print json.dumps(kwargs)
	sys.exit(rc)

def fail_json(**kwargs):
	kwargs['failed'] = True
	exit_json(rc=1, **kwargs)

def run_brew(command):
	try:
		cmd = subprocess.Popen(command, shell=True, 
			stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		out, err = cmd.communicate()
	except (OSError, IOError), e:
		rc = 1
		err = str(e)
		out = ''
	except:
		rc = 1
		err = traceback.format_exc()
		out = ''
	else:
		rc = cmd.returncode
		return rc, out, err

def package_status(pkg):
	cmd = '%s list' % BREW
	rc, out, err = run_brew(cmd)
	if rc:
		fail_json(msg="'brew list' failed: %s" % err)
	for pkgname in out.splitlines():
		if pkg == pkgname:
			return True
	return False

def brew_doctor():
	cmd = '%s doctor' % BREW
	rc, out, err = run_brew(cmd)
	if rc:
		fail_json(msg="'brew doctor' failed: %s" % err)
	return True

def brew_upgrade(pkg=False, force=False):
	cmd = "%s upgrade" % BREW
	if force:
		cmd = "%s -f" % cmd
	if pkg:
		cmd = "%s %s" % (cmd, pkg)
	rc, out, err = run_brew(cmd)
	if rc:
		fail_json(msg="'brew upgrade' failed: %s" % err)
	return True

def brew_install(pkg, force=False, upgrade=False, exists=False, compiler='clang'):
	if exists and upgrade:
		return brew_upgrade(pkg, force)
	elif exists:
		return False
	cmd = "%s install" % BREW
	if force:
		cmd = "%s --force" % cmd
	if use_compiler not in ['llvm', 'gcc']:
		cmd = "%s --use-%s" % (cmd, compiler)
	if pkg:
		cmd = "%s %s" % (cmd, pkg)
	rc, out, err = run_brew(cmd)
	if rc:
		fail_json(msg="'brew install' failed: %s" % err)
	return True

def brew_uninstall(pkg, force=False, exists=False):
	if not exists:
		return False
	cmd = "%s uninstall" % BREW
	if force:
		cmd = "%s --force" % cmd
	if pkg:
		cmd = "%s %s" % (cmd, pkg)
	rc, out, err = run_brew(cmd)
	if rc:
		fail_json(msg="'brew uninstall' failed: %s" % err)
	return True

# ===========================================

# See if brew is in PATH first
if not os.path.exists(BREW):
	fail_json(msg="Cannot find brew")

# Get arguments from ansible
argfile = sys.argv[1]
args 	= open(argfile, 'r').read()
items	= shlex.split(args)

# Log to syslog
syslog.openlog('ansible-%s' % os.path.basename(__file__))
syslog.syslog(syslog.LOG_NOTICE, 'Invoked with %s' % args)

# Check if any arguments given
if not len(items):
	fail_json(msg='the module requires arguments (-a)')
	sys.exit(1)

# Split arguments at = character and place into key/value store
params = {}
for x in items:
	(k, v) = x.split("=", 1)
	params[k] = v

# Get module arguments
state 			= params.get('state', 'installed')
package			= params.get('formula', 
				  params.get('pkg', 
	 			  params.get('package', 
				  params.get('name', None))))
update			= params.get('update', 'no')
doctor 			= params.get('doctor', 'no')
link 			= params.get('link', 'no')
force			= params.get('force', 'no')
use_compiler 	= params.get('compiler', 'clang')

# Verify module arguments
package_exists = False
force_yes = False
changed = False
if package:
	if len(package) < 1:
		fail_json(msg='invalid package name')
	else:
		package_exists = package_status(package)

if state not in ['installed', 'latest', 'removed']:
	fail_json(msg='invalid state')

if update not in ['yes', 'no']:
	fail_json(msg='invalid value for update (requires yes or no -- default is no)')

if doctor not in ['yes', 'no']:
	fail_json(msg='invalid value for doctor (requires yes or no -- default is no)')

if link not in ['yes', 'no']:
	fail_json(msg='invalid value for link (requires yes or no -- default is no)')

if force not in ['yes', 'no']:
	fail_json(msg='invalid value for force (requires yes or no -- default is no)')

if use_compiler not in ['clang', 'llvm', 'gcc']:
	fail_json(msg='invalid compiler (use one of clang, llvm or gcc)')

if force == 'yes':
	force_yes = True

if doctor == 'yes':
	rc, out, err = run_brew("%s doctor" % BREW)
	if rc:
		fail_json(msg="'brew doctor' failed: %s" % err)

if update == 'yes':
	rc, out, err = run_brew("%s update" % BREW)
	if rc:
		fail_json(msg="'brew update' failed: %s" % err)

# Run brew
if state == 'installed' and package:
	changed = brew_install(package, force=force_yes,
			exists=package_exists, compiler=use_compiler)
elif state == 'latest':
	changed = brew_install(package, force=force_yes, upgrade=True, 
			exists=package_exists, compiler=use_compiler)
elif state == 'removed':
	changed = brew_uninstall(package, force=force_yes, exists=package_exists)

exit_json(changed=changed)