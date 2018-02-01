#!/usr/bin/python
#  
#  *******************************************************
#  Copyright VMware, Inc. 2014.  All Rights Reserved.
#  *******************************************************
# 
#  DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
#  WARRANTIES OR CONDITIONS # OF ANY KIND, WHETHER ORAL OR WRITTEN,
#  EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY # DISCLAIMS ANY IMPLIED
#  WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY # QUALITY,
#  NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.

import pyVmomi,pyVim.connect
import sys,getopt

SCRIPT_NAME="guestinfo.py"

def help(exitcode):
    print SCRIPT_NAME,' [Options] --vmname=<vmname> --set_info=<guestinfo_key> --value=<guestinfo_value>'
    print '      Set guestinfo value'
    print
    print SCRIPT_NAME,' [Options] --vmname=<vmname> --get_info=<guestinfo_key>'
    print '      Get guestinfo value'
    print
    print SCRIPT_NAME,' [Options] --list'
    print '      VM list'
    print
    print 'Connection Options:'
    print ' -H <vihost> [-O <port>] [-U <username>] [-P <password>] '
    sys.exit(exitcode)

def main(argv):
 host = 'localhost'
 pwd = ''
 port = 443
 user = 'root'

 try:
    opts, args = getopt.getopt(sys.argv[1:],"hlH:O:U:P:G:V:N:",["vihost=","port=","user_name=","password=","vmname=","set_info=","value=","get_info=","list"])
 except getopt.GetoptError as err:
    # print help information and exit:
    print str(err) # will print something like "option -a not recognized"
    help(2)            
 for opt, arg in opts:
    if opt == '-h':
       help(0)
    elif opt in ("-H", "--vihost"):
       host = arg
    elif opt in ("-O", "--port"):
       port = arg 
    elif opt in ("-U", "--user_name"):
       user = arg
    elif opt in ("-N", "--vmname"):
       vmname = arg
    elif opt in ("-P", "--password"):
       pwd = arg
    elif opt in ("-l", "--list"):
       listVM = 1
    elif opt in ("-P","--set_info"):
       set_info = arg
    elif opt in ("-V","--value"):
       set_info_value = arg
    elif opt in ("-G","--get_info"):
       get_info = arg  
	   
 if not 'listVM' in locals():
            
    if not 'set_info' in locals() or not 'set_info_value' in locals():
       if not 'get_info' in locals():
        help(2)
 
    if not 'vmname' in locals():
     help(3)
  
    
 si = pyVim.connect.Connect(host=host, port=port,
                           user=user, pwd=pwd)
 content = si.RetrieveContent()
 datacenter = content.rootFolder.childEntity[0]
 vmFolder = datacenter.vmFolder
 vmList = vmFolder.childEntity

 if 'listVM' in locals():
    for i in vmList:
       print i.name
    sys.exit(0)
       
 for i in vmList:
         if i.name == vmname:
             vm = i
 if not 'vm' in locals():
    print "Error:Virtual Machine "+vmname+" not found"
    sys.exit(4)

 if  'set_info' in locals():
   cspec = pyVmomi.vim.vm.ConfigSpec()
   cspec.extraConfig = [pyVmomi.vim.option.OptionValue(key=set_info, value=set_info_value)]
   vm.Reconfigure(cspec)

 if  'get_info' in locals():
    cspec = vm.config.extraConfig
    for i in cspec:
        if i.key == get_info:
           print i.value
           sys.exit(0)     
             


if __name__ == "__main__":
   main(sys.argv[1:])


