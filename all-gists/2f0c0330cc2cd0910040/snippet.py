#!/usr/bin/python
from sys import argv
from androguard.core.bytecodes import apk
from androguard.core.bytecodes import dvm
if __name__=="__main__":
	a = apk.APK(argv[1])
	d = dvm.DalvikVMFormat(a.get_dex())
	for current_class in d.get_classes():
		for method in current_class.get_methods():
			print "[*] ",method.get_name(), method.get_descriptor()
			byte_code = method.get_code()
			if byte_code != None:
				byte_code = byte_code.get_bc()
				idx = 0
				for i in byte_code.get_instructions():
					print "\t, %x " % (idx),i.get_name(),i.get_output()
					idx += i.get_length()