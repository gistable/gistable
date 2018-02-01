"""ssh-copy-id for Windows.

Example usage: python ssh-copy-id.py ceilfors@my-remote-machine

This script is dependent on msysgit by default as it requires scp and ssh.
For convenience you can also try that comes http://bliker.github.io/cmder/.
"""

import argparse, os
from subprocess import call

def winToPosix(win):
	"""Converts the specified windows path as a POSIX path in msysgit.

	Example:
	win: C:\\home\\user
	posix: /c/home/user
	"""
	posix = win.replace('\\', '/')
	return "/" + posix.replace(':', '', 1)

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--identity_file", help="identity file, default to ~\\.ssh\\idrsa.pub", default=os.environ['HOME']+"\\.ssh\\id_rsa.pub")
parser.add_argument("-d", "--dry", help="run in the dry run mode and display the running commands.", action="store_true")
parser.add_argument("remote", metavar="user@machine")
args = parser.parse_args()

local_key = winToPosix(args.identity_file)
remote_key = "~/temp_id_rsa.pub"

# Copy the public key over to the remote temporarily
scp_command = "scp {} {}:{}".format(local_key, args.remote, remote_key)
print(scp_command)
if not args.dry:
	call(scp_command)

# Append the temporary copied public key to authorized_key file and then remove the temporary public key
ssh_command = ("ssh {} "
	             "mkdir ~/.ssh;"
	             "touch ~/.ssh/authorized_keys;"
	             "cat {} >> ~/.ssh/authorized_keys;"
	             "rm {};").format(args.remote, remote_key, remote_key)
print(ssh_command)
if not args.dry:
	call(ssh_command)