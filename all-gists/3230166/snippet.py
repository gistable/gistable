#!/usr/bin/env python

"""
- Create a virtualenv in the directory containing this file.
- Activate the above virtualenv
- Install the dependencies for the app, as declared in
  requirements.txt
"""

import os
import sys
import subprocess

from virtualenv import main

def virtualenv_setup(dirpath):
  print "Installing virtualenv..."
  # add the dirpath to the argument vector for virtualenv to work 
  sys.argv.append(dirpath)
  
  # setup the virtualenv
  main()

  return


def append_envvars(dirpath, actpath):
  print "Appending enviroment variables to virtualenv" 
  # append envvars to bin/activate 
  activate_script = open(actpath, 'a')
  activate_script.write("""\n
DJ_DEBUG="False"
DJ_APPROOT={approot}

DJ_DATABASE_ENGINE="django.db.backends." # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
DJ_DATABASE_NAME=""
DJ_DATABASE_USER=""
DJ_DATABASE_PASSWORD=""
DJ_DATABASE_HOST=""
DJ_DATABASE_PORT=""

DJ_TIME_ZONE="Asia/Kolkata"

DJ_SECRET_KEY="_5^wzr#ms%new!sq93tb29dy7rlk(6ox1$557rgy8#)p$)fj#1"
""".format(approot=dirpath))

  return


def pip_install(pippath, reqpath):
  # install the dependencies for the app
  subprocess.call([pippath, 'install', '-r', reqpath])

  return

if __name__ == "__main__":
  # Figure out the directory to which to install the virtualenv
  filepath = os.path.realpath(__file__)
  dirpath  = os.path.dirname(filepath)
  actpath  = os.path.join(dirpath, 'bin', 'activate')
  pippath  = os.path.join(dirpath, 'bin', 'pip')
  reqpath  = os.path.join(dirpath, 'requirements.txt')

  flags = {
      'virtualenv': False
  }

  # check for existing installation of virtualenv
  if os.path.exists(actpath):
    flags['virtualenv'] = True

  if not flags['virtualenv']:
    # install the virtualenv and also append to the path
    virtualenv_setup(dirpath)
    append_envvars(dirpath, actpath)
    pip_install(pippath, reqpath)

    sys.exit('Done')

  # other than the default scheme of things, if an argument
  # 'dependencies' has been supplied, reinstall the 
  if len(sys.argv) > 1 and sys.argv[1] == 'dependencies':
    pip_install(pippath, reqpath)

  # also, if append_envvars has been done, print out the messsage
  if not flags['virtualenv']:
    print """
    Environment specific configuration variables have been added to
    the end of the bin/activate script.  Please update them to the
    current resource handles and values depending on the current
    deployment scheme.
    """