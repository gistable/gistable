#! /usr/bin/env python

# Simple command script to download and add Google Material
# Design Icons ( https://www.google.com/design/icons/ ) to
# to your Android project.
# 'gmid' stands for 'Google Material Icons Downloader'

import sys
import os

# Constants
FILE_PATTERN = 'ic_{}_{}_{}'
BASE_URL_PATTERN = "https://storage.googleapis.com/material-icons/external-assets/v2/icons/zip/"
DEFAULT_COLOR = 'white'
DEFAULT_SIZE = '24dp'
DEFAULT_RES_PATH = './app/src/main/res'

def generate_url (name, color, size):
  return BASE_URL_PATTERN + FILE_PATTERN.format(name, color, size) + '.zip'

args = sys.argv[1:]

# Show usage instructions
if (len(args) == 0):
  print 'Command line tool to download Google Material Icons ( https://www.google.com/design/icons/ )'
  print ''
  print 'Usage (in project root):'
  print '$ chmod +x gmid.py'
  print '$ ./gmid.py icon_name [color=white] [size=24dp] [resources_path=./app/src/main/res]'
  print ''
  print 'Examples :'
  print '$ ./gmid.py copyright'
  print '$ ./gmid.py content_copy black 48dp'
  sys.exit()

# Get the arguments
name = args[0]
color = args[1] if len(args) > 1 else DEFAULT_COLOR
size = args[2] if len(args) > 2 else DEFAULT_SIZE
res_path = args[3] if len(args) > 3 else DEFAULT_RES_PATH

# More constants
SUPPORTED_SIZES = [ '18', '24', '36', '48' ]
SUPPORTED_SIZES_DP = [ s + 'dp' for s in SUPPORTED_SIZES ]
SUPPORTED_COLORS = [ 'white', 'black' ]
CURL_COMMAND = 'curl -s {} -o /tmp/gmid/{}.zip'
UNZIP_COMMAND = 'unzip -q -o /tmp/gmid/{}.zip -d /tmp/gmid/'
MV_COMMAND = 'mv /tmp/gmid/{}/android/{}/{}.png {}/{}/{}.png'

# Download and unzip the icons file to /tmp/gmid
url = generate_url(name, color, size)
print 'Fetching icons from:', url, "\n"
fname = FILE_PATTERN.format(name, color, size)
os.system('mkdir -p /tmp/gmid')
os.system(CURL_COMMAND.format(url, fname))
os.system(UNZIP_COMMAND.format(fname))

# Get the size-based directory names
(_, dirnames, _) = os.walk('/tmp/gmid/' + fname + '/android/').next()

def make_mv_command(dirname, fname):
  return MV_COMMAND.format(fname, dirname, fname, res_path, dirname, fname)

def make_mkdir_command(dirname):
  return "mkdir -p {}/{}".format(res_path, dirname)

# Move the icons to the right location
for dir in dirnames:
  os.system(make_mkdir_command(dir))
  os.system(make_mv_command(dir, fname))


