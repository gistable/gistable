#! /usr/bin/env python
# coding:utf-8

import subprocess

p = subprocess.Popen(['pgrep', '--count', 'conky'], shell=False, stdout=subprocess.PIPE)
p.wait()
if p.communicate()[0] == b'0\n' :
	subprocess.Popen('conky', shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
	#start conky 2
	#start conky 3
if p.communicate()[0] == b'1\n' :
	#start conky 2
	#start conky 3
if p.communicate()[0] == b'2\n' :
	#start conky 3 


