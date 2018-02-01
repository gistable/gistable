#!/usr/bin/env python

"""
  Author: Vivek Ramachandran
	Website: http://SecurityTube.net
	Online Infosec Training: http://SecurityTube-Training.com

"""

import paramiko
import sys

def UploadFileAndExecute(sshConnection, fileName) :

	sftpClient = ssh.open_sftp()
	
	sftpClient.put(fileName, "/tmp/" +fileName)

	ssh.exec_command("chmod a+x /tmp/" +fileName)

	ssh.exec_command("nohup /tmp/" +fileName+ " &")


if __name__ == "__main__" :
	
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(sys.argv[1], username=sys.argv[2], password=sys.argv[3])
	
	UploadFileAndExecute(ssh, sys.argv[4])
	
	ssh.close()
  