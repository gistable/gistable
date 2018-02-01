#!/usr/bin/env python
#
# This script will launch the Cisco AnyConnect Mobility Client from the
# command line, and using credentials stored in the the user's Logon Keychain,
# will initiate a connection to the VPN endpoint.
# 
# Requirements:
# - Cisco AnyConnect Mobility Client is assumed to be installed, and in its
# default location.
# - Python 'keyring' package is assumed to be installed.  Please see
# https://pypi.python.org/pypi/keyring for more information.
# - Python 'pexpect' package is assumed to be installed.  Please see
# https://github.com/pexpect/pexpect for more information.
# - You must walk through a manual CLI connection at least once in order to
# know what to populate the below variables with.  You can do that by
# executing `/opt/cisco/anyconnect/bin/vpn connect <hostname or ip address>` 
# Specifically, take note of the Group Number that you wish this script to
# connect to.  That number will need to be added to the vpngroup variable in
# the next section.
# 
# 
# v 0.9 2014-02-07 bill@wellingtonnet.net

# setup these variables
address = ''    # The hostname or IP of the VPN device you are trying to connect to
vpngroup = ''   # The VPN group you are trying to connect to (numerical)
username = ''   # This is the username for the vpn connection
sysname = ''    # This is the name of the entry in Keychain that stores your credentials


################################################################################
#### Do not edit below this line ###############################################
################################################################################
# import some modules
import sys
import os

try:
  import keyring
except ImportError:
  sys.stderr.write("You do not have 'keyring' installed.  Please see https://pypi.python.org/pypi/keyring for more information.")
  exit(1)
  
try:
  import pexpect
except ImportError:
  sys.stderr.write("You do not have 'pexpect' installed.  Please see https://github.com/pexpect/pexpect for more information.")
  exit(1)

# Alright, let's get to work!

def get_password(sysname, username):
  return keyring.get_password(sysname, username)
  
def connection(address, vpngroup, username, password):
  child = pexpect.spawn('/opt/cisco/anyconnect/bin/vpn connect ' + address, maxread=2000)
  child.logfile = sys.stdout
  child.expect('Group: \[.*\]')
  child.sendline(vpngroup)
  child.expect('Username: \[.*\]')
  child.sendline(username)
  child.expect('Password:')
  child.logfile = None
  child.sendline(password)
  child.logfile = sys.stdout
  child.expect('  >> notice: Please respond to banner.')
  child.delaybeforesend = 1
  child.sendline('y')
  child.expect('  >> state: Connected')

def launchGUI():
  os.system('open -a "Cisco AnyConnect Secure Mobility Client"')
  
def main():
  password = get_password(sysname, username).encode('ascii')
  connection(address, vpngroup, username, password)
  launchGUI()  

# call main()
if __name__ == '__main__':
  main()