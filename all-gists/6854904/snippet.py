#!/usr/bin/python

import sys
import os, shutil
import subprocess
import os.path
from datetime import datetime

######################## Functions #########################

def photoDate(f):
  "Return the date/time on which the given photo was taken."

  cDate = subprocess.check_output(['sips', '-g', 'creation', f])
  cDate = cDate.split('\n')[1].lstrip().split(': ')[1]
  return datetime.strptime(cDate, "%Y:%m:%d %H:%M:%S")


###################### Main program ########################

# Where the photos are and where they're going.
sourceDir = os.environ['HOME'] + '/Pictures/iPhone Incoming'
destDir = os.environ['HOME'] + '/Pictures/iPhone'
errorDir = destDir + '/Unsorted/'

# The format for the new file names.
fmt = "%Y-%m-%d %H-%M-%S"

# The problem files.
problems = []

# Get all the JPEGs in the source folder.
photos = os.listdir(sourceDir)
photos = [ x for x in photos if x[-4:] == '.jpg' or x[-4:] == '.JPG' ]

# Prepare to output as processing occurs
lastMonth = 0
lastYear = 0

# Create the destination folder if necessary
if not os.path.exists(destDir):
  os.makedirs(destDir)
if not os.path.exists(errorDir):
  os.makedirs(errorDir)

# Copy photos into year and month subfolders. Name the copies according to
# their timestamps. If more than one photo has the same timestamp, add
# suffixes 'a', 'b', etc. to the names. 
for photo in photos:
  # print "Processing %s..." % photo
  original = sourceDir + '/' + photo
  suffix = 'a'
  try:
    pDate = photoDate(original)
    yr = pDate.year
    mo = pDate.month

    if not lastYear == yr or not lastMonth == mo:
      sys.stdout.write('\nProcessing %04d-%02d...' % (yr, mo))
      lastMonth = mo
      lastYear = yr
    else:
      sys.stdout.write('.')
    
    newname = pDate.strftime(fmt)
    thisDestDir = destDir + '/%04d/%02d' % (yr, mo)
    if not os.path.exists(thisDestDir):
      os.makedirs(thisDestDir)

    duplicate = thisDestDir + '/%s.jpg' % (newname)
    while os.path.exists(duplicate):
      newname = pDate.strftime(fmt) + suffix
      duplicate = destDir + '/%04d/%02d/%s.jpg' % (yr, mo, newname)
      suffix = chr(ord(suffix) + 1)
    shutil.copy2(original, duplicate)
  except Exception:
    shutil.copy2(original, errorDir + photo)
    problems.append(photo)
  except:
    sys.exit("Execution stopped.")

# Report the problem files, if any.
if len(problems) > 0:
  print "\nProblem files:"
  print "\n".join(problems)
  print "These can be found in: %s" % errorDir
