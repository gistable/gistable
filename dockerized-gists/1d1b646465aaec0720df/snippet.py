#!/usr/bin/python
# -*- coding: UTF-8
# 
# shiba256 - the shiba 256bit hash (such hash, so secure, much crypto)
#
#---------▄--------------▄
#--------▌▒█-----------▄▀▒▌
#--------▌▒▒▀▄-------▄▀▒▒▒▐
#-------▐▄▀▒▒▀▀▀▀▄▄▄▀▒▒▒▒▒▐
#-----▄▄▀▒▒▒▒▒▒▒▒▒▒▒█▒▒▄█▒▐
#---▄▀▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▀██▀▒▌
#--▐▒▒▒▄▄▄▒▒▒▒▒▒▒▒▒▒▒▒▒▀▄▒▒▌
#--▌▒▒▐▄█▀▒▒▒▒▄▀█▄▒▒▒▒▒▒▒█▒▐
#-▐▒▒▒▒▒▒▒▒▒▒▒▌██▀▒▒▒▒▒▒▒▒▀▄▌
#-▌▒▀▄██▄▒▒▒▒▒▒▒▒▒▒▒░░░░▒▒▒▒▌
#-▌▀▐▄█▄█▌▄▒▀▒▒▒▒▒▒░░░░░░▒▒▒▐
#▐▒▀▐▀▐▀▒▒▄▄▒▄▒▒▒▒▒░░░░░░▒▒▒▒▌
#▐▒▒▒▀▀▄▄▒▒▒▄▒▒▒▒▒▒░░░░░░▒▒▒▐
#-▌▒▒▒▒▒▒▀▀▀▒▒▒▒▒▒▒▒░░░░▒▒▒▒▌
#-▐▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▐
#--▀▄▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▄▒▒▒▒▌
#----▀▄▒▒▒▒▒▒▒▒▒▒▄▄▄▀▒▒▒▒▄▀
#---▐▀▒▀▄▄▄▄▄▄▀▀▀▒▒▒▒▒▄▄▀
#--▐▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▀▀
#
import hashlib
import sys

def shiba2 (data):
	sha2 = lambda (d): hashlib.sha256 (d).hexdigest ()
	l = []
	hs = ''
	if len (data) < 5:
		data += 'z' * (5 - len (data))
	for i in range (0, len(data), 4):
		if i > 4:
			cs = sha2 (data[i:i+4] + data[i-8:i])
		else:
			cs = sha2 (data[i:i+4])
		l.append (list (cs))
	while len (hs) < 64:
		for h in l[::-1]:
			hs += h.pop () + h.pop () + h.pop ()

	return hs[0:64]
			
if __name__ == "__main__":
	if len (sys.argv) == 2:
		print shiba2 (sys.argv[1])
	else:
		print 'usage:',sys.argv[0],'message'
	
