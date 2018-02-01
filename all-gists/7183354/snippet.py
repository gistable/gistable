import re
import sys
import pefile
from pydbg import *
from pydbg.defines import *

def parseidalog(file):
	all_funcs = []
	f = open(file)
	funcs = f.readlines()
	f.close()
	for func in funcs:
		if 'sub_' in func:
			m = re.search('.text .+ 0', func)
			addr = '0x'+m.group(0)[6:-2].replace('\n','')
			addr = int(addr, 16)
			all_funcs.append(addr)
	return all_funcs
def printeip(dbg):
	eip = dbg.context.Eip
	if eip not in most_used_funcs:
		most_used_funcs.append(eip)
		print 'Break Point Hit  ', hex(eip)
	return DBG_CONTINUE
def setallbp(dbg):
	for fun in all_func:
		#print '[+] Setting soft bp on ',hex(fun)
		dbg.bp_set(fun,handler=printeip)
	return DBG_CONTINUE
def main():
	global all_func
	global most_used_funcs
	most_used_funcs = []
	all_func = parseidalog('ida-export.txt')
	dbg = pydbg()
	exe_file = sys.argv[1]
	pe = pefile.PE(exe_file)
	dbg = pydbg()
	dbg.load(exe_file)
	entry = pe.OPTIONAL_HEADER.ImageBase + pe.OPTIONAL_HEADER.AddressOfEntryPoint
	dbg.bp_set(entry,handler=setallbp)
	dbg.run()

if __name__ == '__main__':
	main()