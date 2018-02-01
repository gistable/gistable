#!/usr/bin/env python

from ftplib import FTP
from time import sleep
import os

my_dirs = []  # global
my_files = [] # global
curdir = ''   # global

def get_dirs(ln):
  global my_dirs
  global my_files
  cols = ln.split(' ')
  objname = cols[len(cols)-1] # file or directory name
  if ln.startswith('d'):
    my_dirs.append(objname)
  else:
    if objname.endswith('.zip'):
      my_files.append(os.path.join(curdir, objname)) # full path

def check_dir(adir):
  global my_dirs
  global my_files # let it accrue, then fetch them all later
  global curdir
  my_dirs = []
  gotdirs = [] # local
  curdir = ftp.pwd()
  print("going to change to directory " + adir + " from " + curdir)
  ftp.cwd(adir)
  curdir = ftp.pwd()
  print("now in directory: " + curdir)
  ftp.retrlines('LIST', get_dirs)
  gotdirs = my_dirs
  print("found in " + adir + " directories:")
  print(gotdirs)
  print("Total files found so far: " + str(len(my_files)) + ".")
  sleep(1)
  for subdir in gotdirs:
    my_dirs = []
    check_dir(subdir) # recurse  
    
  ftp.cwd('..') # back up a directory when done here
  
try:
  ftp = FTP('ftp2.census.gov')
  ftp.login()
  check_dir('/geo/tiger/GENZ2012') # directory to start in
  ftp.cwd('/.') # change to root directory for downloading
  for f in my_files:
    print('getting ' + f)
    file_name = f.replace('/', '_') # use path as filename prefix, with underscores
    ftp.retrbinary('RETR ' + f, open(file_name, 'wb').write)
    sleep(1)
except:
  print('oh dear.')
  ftp.quit()

ftp.quit()
print('all done!')
