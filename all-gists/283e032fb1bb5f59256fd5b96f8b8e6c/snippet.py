#!/usr/bin/python

from plistlib import readPlist as read_plist
from subprocess import check_output
import socket
import json
from datetime import datetime
import os

# Export your version of these for testing the script from the console directly:
# During build, this is run in the iOS directory by the Environment Switch Task
# target.

# SCHEME_FILE is set by an environment variable on the YOURAPP project and is written
# as a pre-build command by the individual schemes.
#
# To edit the environment variable, go to the bottom of YOURAPP -> Build Settings in the
# project tab of XCode.
#
# To modify the writing of a temp file that stores the currently-building scheme name, go to
# Edit Schemes -> Build -> Pre-build.
scheme = check_output(['cat', os.environ['SCHEME_FILE']]).strip()

# Whitelist scheme names:
if scheme not in ['Development', 'Testflight', 'Production']:
 raise StandardError.new('Scheme must be one of Development, Testflight, or Production. If you need another, whitelist it in iOS/Configuration/build-environment.py')

# Get directories:
project_dir = os.environ['PROJECT_DIR']
config_dir = os.path.join(project_dir,'iOS','Configuration')

# This is the location of, say "environment_SchemeName.plist". We gitignored
# "environment_Development.plist" and instead committed "environment_Development.plist.sample"
# So that each dev's config doesn't get committed.
env_plist = os.path.join(config_dir, 'environment_%s.plist' % scheme)

# Read the environment plist, e.g. environment_Development.plist:
conf = read_plist(env_plist)

# Put the scheme and project directory into env config:
conf['FS_ENVIRONMENT'] = scheme
conf['FS_PROJECT_DIR'] = os.environ['PROJECT_DIR']

# Override for using localhost in ip address lookup:
if 'FS_FORCE_LOCALHOST' not in conf:
  conf['FS_FORCE_LOCALHOST'] = False

# Override for using localhost in ip address lookup:
if 'FS_USE_API_HOST' not in conf:
  conf['FS_FORCE_LOCALHOST'] = 'FS_API_HOST' in conf

if 'FS_USE_BUNDLED_JS' not in conf:
  conf['FS_USE_BUNDLED_JS'] = False

# Get the local ip address:
host = None
def get_host(port=None):
  # cache the ip address even though I think it does that internally:
  global host

  if host is None:
    if conf['FS_FORCE_LOCALHOST']:
      # Localhost override:
      host = 'localhost'
    else:
      # Look up the ip address, attempting to exclude virtual hosts:
      host_ex = socket.gethostbyname_ex(socket.gethostname())
      host = host_ex[-1][-1] #[host_ex.index(socket.gethostname())]

  # Prepend http://
  result = 'http://%s' % host

  # Append optional port:
  if port is not None:
    result += ':%s' % port

  return result
  
  
# If it's not set manually, compute the api host address:
if 'FS_API_HOST' not in conf or not conf['FS_USE_API_HOST']:
  conf['FS_API_HOST'] = '%s/api/v7' % get_host(3000)

# Ditto code host:
if not conf['FS_USE_BUNDLED_JS'] and 'FS_CODE_HOST' not in conf:
  conf['FS_CODE_HOST'] = '%s/index.ios.bundle?platform=ios&dev=true' % get_host(8081)
else:
  conf['FS_CODE_HOST'] = ''


# This is a header file so the iOS knows about preprocessor defines:
def export_to_header(filename, data, NSString=False):
  prefix,suffix = ('@"','"') if NSString else ('','')
  f = open(filename,'w')
  f.write('//-----------------------------------------\n')
  f.write('// Auto generated file\n')
  f.write('// Created %s\n' % datetime.strftime(datetime.now(),'%c'))
  f.write('//-----------------------------------------\n\n')
  for key in data:
    val = data[key]
    if isinstance(val,bool):
      val = 'true' if val else 'false'
    else:
      val = '%s%s%s' % (prefix,str(val),suffix)
    f.write('#define %-30s %s\n' % (key, val))
  f.close()

def export_to_json(filename,data):
  f = open(filename,'w')
  f.write('module.exports=%s' % json.dumps(data))
  f.close()

# Export a file for use in the main Info.plist. This let's you do fun stuff like
# set the app name dynamically so that it can be scheme-dependent. To use this, find
# the 'Info.plist Preprocessor Prefix File' build setting for your project and set it
# to this file. Then set 'Preprocess Info.plist File' = Yes.
export_to_header('environment_for_infolist_prefix.h', conf, False)

# This is for plain old objective-c preprocessor defines. The only difference is that
# it needs extra @"" NSString stuff. For regular c #includes.
export_to_header('environment.h', conf, True)

# This is the version that gets exported to json so that json knows about the same config:
export_to_json('../app/config/environment.ios.js', conf)
