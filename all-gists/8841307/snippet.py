######
# author: Stefan McKinnon Edwards <stefan.hoj-edwards@agrsci.dk>
# id: $Id: qsub1.py 25 2013-04-12 11:06:47Z sme $
# qsub-module;
# communicates with cluster-queueing system to retrieve information
# about the current job.
# The qsub commands do no exist on the nodes, so to retrieve the necessary information, 
# we ssh the host and request the information from `qstat`.
#
# To use this module from a script running on a computation cluster,
# be aware that some systems start up a new session from the submitting users home directory.
# I.e. this file cannot a priori be located in the same folder as the script.
# Place instead this module in your local site-packages and it will be available from all scripts (that you run)
# The site-packages directory could be found in linux under ~/.local/lib/pythonx.y/site-packages
#####
from __future__ import print_function
import os
import shlex
import subprocess as sp
from time import time, strptime, mktime, strftime, gmtime
from Path import Path
import tempfile
import sys
import argparse

#module "constants", set during load, only set once.
jobid = os.environ.get('PBS_JOBID', None)
jobint = (jobid.split('.')[0] if jobid is not None else 0)
jobname = os.environ.get('PBS_JOBNAME', None)
isjob = jobid is not None
workdir = Path(os.environ.get('PBS_O_WORKDIR', '.'))
starttime = time()  # ~ mtime, start_time
tmpdir = Path('/scratch/{user}/{jobid}'.format(user=os.environ.get('USER', ''), jobid=jobid))
if not tmpdir.isdir:
  tmpdir = tempfile.mkdtemp()

## constants that require qstat output
qstat_str = None
qstat = None
_corrected_starttime = None
total_walltime = None
total_walltime_seconds = None
ncpus = None
submit_args = None
args = None

## epilog for argparse.ArgumentParser(..., epilog=epilog)
epilog = """This script can be submitted to qsub with the command:
qsub -v args="<commandline arguments>" <script_name>
i.e. the reverse of
python <scriptname> <commandline arguments>
"""

def stime(s):
  ''' Formats a number of seconds into H:M:S. '''
  if s is None:
    return '--:--:--'
  s = int(s)
  h = s / 3600
  m = (s - h * 3600) / 60
  s = s - (h * 3600 + m * 60)
  return '{:02d}:{:02d}:{:02d}'.format(h, m, s)

def used_walltime():
  ''' Returns a corrected estimate of how much time has been used. '''
  if _corrected_starttime is None:
    return None
  return time() - _corrected_starttime

def remaining_walltime():
  ''' Returns seconds left of walltime. '''
  if total_walltime_seconds is None or used_walltime() is None:
    return None
  return total_walltime_seconds - used_walltime()

  

def parse_qstat(qstat_str):
  global total_walltime, total_walltime_seconds, used_walltime, remaining_walltime, ncpus, starttime, _corrected_starttime, qstat, submit_args
  
  qstat = [s.strip() for s in qstat_str.split('\n')]
  qstat = [s.split(' = ') for s in qstat]
  qstat = {l[0]:l[1] for l in qstat if len(l) == 2}

  varlist = qstat['Variable_List'] 
  varlist = varlist.split(',')
  varlist = [v.split('=', 1) for v in varlist]
  qstat['Variable_List'] = {l[0]:l[1] for l in varlist if len(l) == 2}
  
  starttime = mktime(strptime(qstat['mtime']))
  
  total_walltime = qstat['Resource_List.walltime']
  total_walltime_seconds = [int(i) for i in total_walltime.split(':')]
  total_walltime_seconds = 3600*total_walltime_seconds[0] + 60*total_walltime_seconds[1] + total_walltime_seconds[2]
 
  if qstat.has_key('ressources_used.walltime'): 
    walltime_used = [int(i) for i in qstat['resources_used.walltime'].split(':')]  # True used walltime at time of invokation.
    walltime_used = 3600*walltime_used[0] + 60*walltime_used[1] + walltime_used[2] 
  else:
    walltime_used = time() - starttime
  #walltime_used = max(time()-starttime,  walltime_used+starttime)  # Update to longest possible used time?
  _corrected_starttime = min(starttime, time()-walltime_used)
  
  ncpus = qstat['Resource_List.ncpus']
  submit_args = qstat['submit_args']
  
  


def start(fail_on_ssh=True, setwd=True, info=True):
  global qstat_str, walltime, ncpus, walltime_used
  if not isjob:
    if info:
      print_info()
    return False

  # try to extract information  
  # TODO: replace <host name> with address to the host
  try:
    ssh = sp.check_output(['ssh', <host name>,'-o StrictHostKeyChecking yes', 'qstat', '-f -1', os.environ['PBS_JOBID']], shell=False)
    #with open('qstat.txt') as fin:
    #  ssh = fin.read()
  except BaseException as e:
    if fail_on_ssh:
      raise
    else:
      return False
  
  qstat_str = ssh
  try:
    parse_qstat(ssh)
  except:
    print(ssh)
    raise

  if setwd and qstat.get('interactive', 'False') != 'True':
    os.chdir(workdir)
    
  if info:
    print_info()
  return True

def print_info():
  print('Job name:', jobname)
  print('Job ID:  ', jobid)
  print('Started: ', strftime("%a %b %d %H:%M:%S %Y", gmtime(starttime)))
  print('Work dir:', os.getcwd())
  print('Temp dir:', tmpdir) 
  print('Submit args:', submit_args)
  #print('')
  
  
def stop(status=0, exitmsg=None):
  ''' Will print some statistics. '''
  print('-- End of job --')
  print('Stopped:  ', strftime("%a %b %d %H:%M:%S %Y"))
  print('Time used:', stime(used_walltime()))
  if status != 0:
    print('Stopped with exit status', status)
  if exitmsg is not None:
    print(exitmsg)
  sys.exit(status)

def stop_wanted(location):
  if location == 'tmp':
    loc = tmpdir
  elif location == 'workdir':
    loc = workdir
  else:
    loc = Path(location)  

  return loc.append('STOP').exists
  
  
def add_to_searchpath(p):
  ''' Adds path p to Python's search path. If p is relative path, it is relative to working directory! '''
  p = Path(p)
  if p.isdir:
    sys.path.append(p.abspath)
 

def parse_args(parser):
  ''' 
  Uses, if available, environment variable `args` as commandline source.
  Returns dictionary so it can be used as mapping for function call.
  '''
  if isjob and os.environ.has_key('args'):
    args = parser.parse_args(shlex.split(os.environ['args']))
  else:
    args = parser.parse_args()
  return vars(args)
