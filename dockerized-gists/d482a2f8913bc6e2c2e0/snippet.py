#!/usr/bin/env python3
"""Usage: vimcrypt.py [FILE]...

Guesses first 64 bytes of vim-encrypted files. Method implemented is sufficient
for plain English (preferably with lots of spaces), but any knowledge of
underlying plaintext would do.

Example:

$ ./vimcrypt.py 1.txt 2.txt 3.txt 4.txt
1.txt:
  '                                ==Phrack Inc.==\r\n               '
2.txt:
  'Vim is able to write files encrypted, and read them back.  The e'
3.txt:
  'reddit         qwerty\r\ntwitter        12345\r\nfacebook       abc1'
4.txt:
  '     Re ipes fo1 Nonsur5ival - \x17he Anar hist Co,kbook b: Willia.'
"""
import fileinput, sys

xor = lambda a,b:bytes([x^y for x,y in zip(a,b)])

W = {'\t': 32, '\n': 107, '\r': 107, '!': 5, ' ': 936, '"': 30, '%': 1, "'":
33, ')': 2, '(': 2, '+': 1, '*': 14, '-': 13, ',': 41, '/': 6, '.': 58, '1': 7,
'0': 6, '3': 5, '2': 2, '4': 1, '7': 1, '6': 1, '9': 3, '8': 7, ':': 17, '=':
6, '>': 6, 'A': 9, 'C': 3, 'E': 8, 'D': 2, 'G': 2, 'I': 12, 'O': 1, 'N': 6,
'P': 7, 'S': 5, 'R': 1, 'U': 2, 'T': 25, 'W': 8, 'V': 10, 'Y': 4, 'X': 4, 'a':
201, 'c': 114, 'b': 62, 'e': 568, 'd': 123, 'g': 53, 'f': 91, 'i': 273, 'h':
194, 'k': 57, 'j': 1, 'm': 104, 'l': 132, 'o': 278, 'n': 249, 'q': 1, 'p': 104,
's': 184, 'r': 205, 'u': 97, 't': 414, 'w': 80, 'v': 30, 'y': 133, 'x': 23,
'{': 1, 'z': 9, '}': 1, '|': 8, '~': 1} # letter frequency in vim manual

def one_byte_xor_key(ciph):
    """Maximizes per-byte metric trained on byte frequency."""
    guesses = [xor(ciph, bytes([k])*8) for k in range(256)]
    scores = [sum([W.get(chr(c), 0) for c in g]) for g in guesses]
    return bytes([scores.index(max(scores))])

def vim_blowfish(s):
    if s.startswith(b'VimCrypt~01!'):
        return 'cryptmethod=zip, see :help encryption'
    if not s.startswith(b'VimCrypt~02!'):
        return 'wrong format'
    chunk = s[28:28+64] # header: [12:magic][8:salt][8:CFB IV]
    # blocks: 8x blowfish CFB streams in parallel, all with the same IV
    block_key = b''.join([one_byte_xor_key(chunk[n::8]) for n in range(8)])
    return repr(xor(chunk, 8*block_key))
    
if __name__ == '__main__':
    if len(sys.argv) is 1:
        print(__doc__)
        exit(0)
    for s in fileinput.input(mode='rb', bufsize=28+64):
        print(fileinput.filename() + ':\n  ' + vim_blowfish(s))
        fileinput.nextfile()