# -*- coding: utf-8 -*-

'''
Steganogrphy in Python
Copyright 2013 Josiah Carlson
Released under the GNU LGPL v2.1 license

What, how, why, etc, are discussed:
http://www.dr-josiah.com/2013/05/steganography-in-python.html

'''

from cStringIO import StringIO
import functools
import getpass
import glob
from hashlib import sha1, sha256
import hmac
import optparse
import re
import tokenize

CODING_RE = re.compile("coding[:=]\s*([-\w.]+)")
CHR = u'\xa0'

def detect_encoding(fobj):
    # Detects the character encoding of a file based on the Python coding
    # declaration. Returns the space replacement encoded and the encoding.
    lines = []
    fobj.seek(0)
    for i, line in enumerate(fobj):
        lines.append(line)
        if i >= 1:
            break
    encoding = CODING_RE.search('\n'.join(lines))
    encoding = encoding.group(1) if encoding else ''
    fobj.seek(0)
    return CHR.encode(encoding) if encoding else '', encoding

def clean(fname, w=False):
    # Cleans a file's contents to have no hidden data. Useful for prepping
    # new data, or prepping to count the available bits in a file.
    inp = StringIO(open(fname, 'rb').read())
    enc = detect_encoding(inp)[0]
    tokens = []
    try:
        for toknum, tokval, _1, _2, _3 in tokenize.generate_tokens(inp.readline):
            if toknum == tokenize.INDENT:
                tokens.append((toknum, tokval.replace('\t', 8*' '), _1, _2, _3))
            elif enc and toknum == tokenize.COMMENT:
                if 'coding:' in tokval or 'coding=' in tokval:
                    tokens.append((toknum, tokval, _1, _2, _3))
                    continue
                tokens.append((toknum, tokval.replace(enc, ' '), _1, _2, _3))
            else:
                tokens.append((toknum, tokval, _1, _2, _3))
    except tokenize.TokenError:
        print "-ERR", fname
        return

    try:
        cleaned = tokenize.untokenize(tokens)
    except AssertionError:
        print "-ERR", fname
        return
    if w:
        with open(fname, 'wb') as out:
            out.write(cleaned)
    return cleaned

def clean_and_pass(f):
    # A quick decorator to clean the content of a file and pass it to a
    # function.
    @functools.wraps(f)
    def cnp(fname, *args, **kwargs):
        inp = kwargs.pop('inp', None)
        if not inp:
            r = clean(fname, False)
            if r is None:
                return
            inp = StringIO(r)
        return f(inp, fname, *args, **kwargs)
    return cnp

def _count(inp):
    # Count the number of bits that can be hidden in a given file. Used to
    # verify that data can actually be embedded.
    enc = detect_encoding(inp)[0]
    count = 0
    for toknum, tokval, _, _, _ in tokenize.generate_tokens(inp.readline):
        if toknum == tokenize.INDENT:
            count += tokval.replace(8*' ', '\t').count('\t')
        elif enc and toknum == tokenize.COMMENT:
            cnt = count
            count += tokval.count(' ')
    return count

@clean_and_pass
def count_bits(inp, fname, p=True):
    # Wrapper that prints the results of the bit counting.
    count = _count(inp)
    if p:
        print count, fname
    return count

@clean_and_pass
def add_bits(inp, fname, hex_data):
    # Actually add bits to a file.
    bits_needed = 8 + len(hex_data) * 4
    bits_available = min(_count(inp), 1032)
    if bits_needed > bits_available:
        print "-ERR %s - %s/%s available"%(fname, bits_needed, bits_available)
        return

    inp.seek(0)
    enc = detect_encoding(inp)[0]
    if enc:
        BITS = [' ', enc]
    hex_data = '%02x'%(len(hex_data)-1) + hex_data
    hex_data = int(hex_data, 16)
    bits = []
    while len(bits) < bits_needed:
        bits.append(hex_data & 1)
        hex_data >>= 1

    tokens = []
    for toknum, tokval, _1, _2, _3 in tokenize.generate_tokens(inp.readline):
        if bits and toknum == tokenize.INDENT and len(tokval) >= 8:
            tv = [tokval[i:i+8] for i in xrange(0, len(tokval), 8)]
            for i in xrange(len(tv)):
                if len(tv[i]) == 8:
                    if bits.pop():
                        tv[i] = '\t'
                if not bits:
                    break
            tokens.append((toknum, ''.join(tv), _1, _2, _3))
        elif enc and bits and toknum == tokenize.COMMENT:
            if 'coding:' in tokval or 'coding=' in tokval:
                tokens.append((toknum, tokval, _1, _2, _3))
                continue
            tv = tokval.split(' ')
            xx = 0
            for i in xrange(len(tv)-1):
                if bits:
                    xx <<= 1
                    xx += bits[-1]
                tv[i] += BITS[bits.pop()] if bits else ' '
            tv = ''.join(tv)
            tokens.append((toknum, tv, _1, _2, _3))
        else:
            tokens.append((toknum, tokval, _1, _2, _3))

    with open(fname, 'wb') as out:
        out.write(tokenize.untokenize(tokens))

def read_bits(fname, p=True):
    # Read bits from a file.
    inp = StringIO(open(fname, 'rb').read())
    encoding = detect_encoding(inp)[1]
    chars = (u' ', CHR)
    bits = 0
    bc = 0
    found = False
    done = False
    for toknum, tokval, _1, _2, _3 in tokenize.generate_tokens(inp.readline):
        if toknum == tokenize.INDENT:
            tdata = tokval.replace('\t', 8*' ')
            if len(tdata) < 8:
                continue
            for i in xrange(0, len(tdata)-7, 8):
                bits <<= 1
                bc += 1
                if tokval.startswith('\t'):
                    bits += 1
                    tokval = tokval[1:]
                else:
                    tokval = tokval[8:]

                if not found and bc == 8:
                    found = 4 * (bits + 1)
                    bits = bc = 0
                elif bc == found:
                    done = True
                    break

        elif toknum == tokenize.COMMENT:
            if 'coding:' in tokval or 'coding=' in tokval:
                continue
            tokval = tokval.decode(encoding)
            bcc = bc
            for ch in tokval:
                if ch not in chars:
                    continue
                bits <<= 1
                bc += 1
                bits += chars.index(ch)

                if not found and bc == 8:
                    found = 4 * (bits + 1)
                    bits = bc = bcc = 0
                elif bc == found:
                    done = True
                    break

        if done:
            break

    found //= 4
    data = ('%%0%sx'%found)%bits
    if p:
        print data, fname
    return data

def _calc_hmac(inp, pw, hfun):
    # Use some key derivation to make the hmac more difficult to crack.
    hash = ''
    for i in xrange(32768):
        hash = hfun(hash + pw + "%02x"%i).digest()

    inp.seek(0)
    return hmac.new(hash, inp.read(), hfun).hexdigest()

@clean_and_pass
def embed_hmac(inp, fname, hfun, w=True):
    # Actually embed an hmac into a file
    required = 8 + hfun().digest_size * 8
    available = _count(inp)
    if available < required:
        print "-ERR %s - %s/%s available"%(fname, required, available)
        return

    pw = getpass.getpass("hmac password:")
    hash = _calc_hmac(inp, pw, hfun)

    if w:
        inp.seek(0)
        add_bits(fname, hash, inp=inp)
    return hash

def check_hmac(fname, hfun):
    # Verify an embedded hmac matches
    digest = read_bits(fname, False)
    hm = embed_hmac(fname, hfun, False)
    if sum(ord(x) ^ ord(y) for x,y in zip(digest,hm)) + (len(digest) ^ len(hm)):
        print '-NOMATCH', fname
    else:
        print '+MATCH', fname

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.usage = "%prog [options] <file, files, or filename mask>"
    parser.add_option('--bits', dest='count', action='store_true', default=False,
                      help="Count the number of available bits in files")
    parser.add_option('--write', dest='write', action='store', default='',
                      help="Add the provided hex data to the file, replacing any previously hidden data")
    parser.add_option('--read', dest='read', action='store_true', default=False,
                      help="Read the bits from the files and return their hex values")
    parser.add_option('--clean', dest='flush', action='store_true', default=False,
                      help="Clean the provided files of hidden bits")
    parser.add_option('--sha1', dest='sha1', action='store_true', default=False,
                      help="Generate the sha1 hmac of the file, and hide the hmac in the file (a password prompt will be provided)")
    parser.add_option('--check-sha1', dest='csha1', action='store_true', default=False,
                      help="Check the embedded sha1 hmac of the file (a password prompt will be provided)")
    parser.add_option('--sha256', dest='sha256', action='store_true', default=False,
                      help="Generate the sha256 hmac of the file, and hide the hmac in the file (a password prompt will be provided)")
    parser.add_option('--check-sha256', dest='csha256', action='store_true', default=False,
                      help="Check the embedded sha256 hmac of the file (a password prompt will be provided)")

    options, args = parser.parse_args()

    # Glob expansion for Windows
    _args = []
    for arg in args:
        _args.extend(glob.glob(arg))
    args = _args
    if not args:
        print "You must provide at least one file to manipulate\n"
        parser.parse_args(['-h'])
        raise SystemExit
    if options.count:
        _ = map(count_bits, args)
    elif options.write:
        add_bits(args[0], options.write)
    elif options.read:
        _ = map(read_bits, args)
    elif options.flush:
        _ = [clean(a, True) for a in args]
    elif options.sha1:
        _ = embed_hmac(args[0], sha1)
    elif options.sha256:
        _ = embed_hmac(args[0], sha256)
    elif options.csha1:
        _ = check_hmac(args[0], sha1)
    elif options.csha256:
        _ = check_hmac(args[0], sha256)
    else:
        print "Nothing to do!\n"
        parser.parse_args(['-h'])
