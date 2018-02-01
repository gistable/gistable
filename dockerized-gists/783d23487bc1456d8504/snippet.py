#!/usr/bin/python

import os
import pexpect
import sys
import shutil
import subprocess

def run(cmd):
  proc = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
  )
  (out, err) = proc.communicate()
  return (out, err)

server = '/Applications/Server.app'
if not os.path.exists(server):
  print >> sys.stderr, 'Server.app is not installed!'
  sys.exit(-1)
server_contents = os.path.join(server, 'Contents')
server_root = os.path.join(server_contents, 'ServerRoot')
serverd_path = 'Library/LaunchServices/com.apple.serverd'
serverd = os.path.join(server_contents, serverd_path)
priv_tool = '/Library/PrivilegedHelperTools'

servercmd = os.path.join(server_root, 'usr/sbin/server')
serveradmin = os.path.join(server_root, 'usr/sbin/serveradmin')

os.makedirs(priv_tool)
shutil.copy(serverd, os.path.join(priv_tool, 'com.apple.serverd'))

# Create a temporary user to use for setting up Server.app
cmd = ['/usr/bin/dscl', '.', 'list', '/Users', 'UniqueID']
(out, err) = run(cmd)
uid_dict = dict(zip(out.split()[0::2], out.split()[1::2]))
# Get the highest current UID and then add one
new_uid = sorted([int(i) for i in uid_dict.values()])[-1] + 1
create_cmd = ['/usr/bin/dscl', '.', 'create']
passwd_cmd = ['/usr/bin/dscl', '.', 'passwd']
serverdotapp_username = 'serverdotappuser'
serverdotapp_pw = 'sup'
picture = "/Library/User Pictures/Fun/Chalk.tif"
user = '/Users/%s' % serverdotapp_username
run(create_cmd.append(user))
run(passwd_cmd.extend([user, serverdotapp_pw]))
run(create_cmd.extend([user, 'UserShell', '/usr/bin/false']))
run(create_cmd.extend([user, 'UniqueID', new_uid]))
run(create_cmd.extend([user, 'PrimaryGroupID', 20]))
run(create_cmd.extend([user, 'RealName', serverdotapp_username]))
run(create_cmd.extend([user, 'Picture', picture]))
run(create_cmd.extend([user, 'Hint', "No hint for you!"]))

# Run the setup tool
server_eula = pexpect.spawn('%s setup' % servercmd)
# server_eula.logfile = sys.stdout
server_eula.expect("Press Return to view the software license agreement.")
server_eula.sendline(' ')
server_eula.expect("(y/N)")
server_eula.sendline('y')
server_eula.expect("User name:")
server_eula.sendline(serverdotapp_username)
server_eula.expect("Password:")
server_eula.sendline(serverdotapp_pw)
server_eula.interact()

# Delete temporary user
cmd = ['/usr/bin/dscl', '.', 'delete', '/Users', serverdotapp_username]
run(cmd)
