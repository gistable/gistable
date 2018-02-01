#!/usr/bin/env python
#coding=utf8

#
# limit_cachedmem.py
# limit cached memory for executing program
#
##########################################################################################
import sys
from os import system
from subprocess import Popen, PIPE
from getopt import getopt
from time import sleep

##########################################################################################
def usage(msg):
	if msg:
		sys.stderr.write('Error:%s\n' % msg)
	sys.stderr.write('''usage: %s [options] exe param [param ...]
  check the cached memory and if exceed the limit then free it
  [options] are:
    -c --cache n : set limit of cached mem to check (MB unit; default is 1024MB)
    -p --period n : set checking period to check (sec unit; default is 5sec)
	-v --verbose : set verbose mode on
	-h --help : show this help message
''' % (sys.argv[0]))
	sys.exit(1)

##########################################################################################
def do_exec(cmds):
	if not isinstance(cmds, list):
		raise ValueError("do_exec(cmds) need list type of cmds")
	po = Popen(cmds)
	return po

##########################################################################################
def get_chched_mem():
	po = Popen(['cat','/proc/meminfo'], stdout=PIPE)
	out = po.stdout.read()
	for line in out.split('\n'):
		eles = line.split()
		if eles[0] == 'Cached:':
			return int(eles[1])/1024 # MB instead kB
	return 0
##########################################################################################
def do(cache=1024, period=5, verbose=False, cmds=[]):
	if not cmds:
		raise ValueError("do_exec(cmds) need executing command and optional parameters")
	if verbose: print('RUN: %s' % cmds)
	po = do_exec(cmds)
	is_break = False
	while not is_break:
		for i in xrange(period):
			if i == 0:
				cmmb = get_chched_mem()
				if cmmb >= cache:
					if verbose: print('EXCEED limit %s <= %s' % (cache, cmmb))
					system('echo 3 > echo 3 > /proc/sys/vm/drop_caches')
				else:
					if verbose: print('NOT EXCEED limit %s > %s' % (cache, cmmb))
			sleep(1)
			returncode = po.poll()
			if returncode is not None: # None means subprocess doing...
				system('echo 3 > echo 3 > /proc/sys/vm/drop_caches') # clear again before quitting
				is_break = True
				break
##########################################################################################
if __name__ == '__main__':
	cmds = None
	nskip = True
	for i, arg in enumerate(sys.argv):
		if nskip:
			nskip = False
			continue
		if arg in ("-c", "--cache", "-p", "--period", ):
			nskip = True
		elif arg in ("-v", "--verbose", "-h", "--help"):
			pass
		else:
			cmds = sys.argv[i:]
			sys.argv = sys.argv[:i]
			break
	if not cmds:
		usage('Run command must not empty')
	kwargs = {'cache':1024, 'period':5, 'verbose':False, 'cmds':cmds}
	try:
		opts, args = getopt(sys.argv[1:], "c:p:vh", ["cache=", "period=", "verbose", "help"])
		for opt, arg in opts:
			if opt in ("-c", "--cache"):
				kwargs['cache'] = int(arg)
			elif opt in ("-p", "--period"):
				kwargs['period'] = int(arg)
			elif opt in ("-v", "--verbose"):
				kwargs['verbose'] = True
			elif opt in ("-h", "--help"):
				usage()
		do(**kwargs)
	except Exception as err:
		usage(str(err))
