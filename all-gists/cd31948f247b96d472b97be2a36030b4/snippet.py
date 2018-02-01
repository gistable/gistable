# Usage: findelevate.py C:\Windows\System32\
# Needs sigcheck.exe in path [https://technet.microsoft.com/en-us/sysinternals/bb897441.aspx]

import sys
import os
import glob
import subprocess

if len(sys.argv) < 2:
	print "Usage: findelevate.py <PATH>"
	print "Ex: Usage: findelevate.py C:\\Windows\\System32\\"
	sys.exit()
	
d = sys.argv[1]

if not (d.endswith('\\')):
	d = d+'\\'

exefiles = []

if os.path.isdir(d):
	exefiles =  glob.glob(d+'*.exe')

i = 0
for exe in exefiles:
	p = subprocess.Popen(['sigcheck', '-nobanner','-m', exe],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	out, err = p.communicate()
	if 'true</autoElevate>' in out: #will check for xmlns autoelevate as well. Thanks @mynameisv_
		print exe.strip()
		i = i + 1

print "Found " + str(i) + " executables with autoElevate set to true!"