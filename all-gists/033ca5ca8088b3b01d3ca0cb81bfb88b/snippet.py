#!/usr/bin/env python3

# usage: cdndownload.py <titleid> [titlekey]
# if a system title is given for titleid, titlekey is not used
# system titles should be "legit CIAs" i.e. a stock system will install it

# unlike other cdn downloaders, this doesn't use make_cdn_cia or anything
# it downloads and saves directly to the cia, so it's faster

import base64
import binascii
import struct
import sys
from urllib.request import urlretrieve, urlopen
import zlib

if len(sys.argv) == 1:
    print("cdndownload.py <titleid> [titlekey]")
    print("- titlekey is only used for non-system titles")
    sys.exit(1)

app_categories = {
    '0000',  # application
    '0002',  # demo
    '000E',  # patch
    '008C',  # DLC
    '8004',  # DSiware
}

tid = sys.argv[1].upper()

if len(tid) != 16:
    print("! title ID is invalid length")
    print("cdndownload.py <titleid> [titlekey]")
    print("- titlekey is only used for non-system titles")
    sys.exit(1)

if tid[4:8] in app_categories:
    if len(sys.argv) != 3:
        print("! missing titlekey")
        print("cdndownload.py <titleid> [titlekey]")
        print("- titlekey is only used for non-system titles")
        sys.exit(1)
    elif len(sys.argv[2]) != 32:
        print("! titlekey is invalid length")
        print("cdndownload.py <titleid> [titlekey]")
        print("- titlekey is only used for non-system titles")
        sys.exit(1)

certchain = zlib.decompress(base64.b64decode(b"""
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
JWFnDuv/P7kyh1k="""))

ticket = "00010004D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0D15EA5E0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000526F6F742D434130303030303030332D585330303030303030630000000000000000000000000000000000000000000000000000000000000000000000000000FEEDFACEFEEDFACEFEEDFACEFEEDFACEFEEDFACEFEEDFACEFEEDFACEFEEDFACEFEEDFACEFEEDFACEFEEDFACEFEEDFACEFEEDFACEFEEDFACEFEEDFACE010000{0}00000000000000000000000000{1}00000010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010014000000AC000000140001001400000000000000280000000100000084000000840003000000000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"

# http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python
#def terminal_size():
#    import fcntl, termios, struct
#    h, w, hp, wp = struct.unpack('HHHH',
#        fcntl.ioctl(0, termios.TIOCGWINSZ,
#        struct.pack('HHHH', 0, 0, 0, 0)))
#    return w, h

# http://stackoverflow.com/questions/8866046/python-round-up-integer-to-next-hundred
def roundup(x, base=64):
    return x if x % base == 0 else x + base - x % base

# some things used from
# http://stackoverflow.com/questions/13881092/download-progressbar-for-python-3
blocksize = 10*1024
def download(url, printprogress=False, outfile=None):
    #print(url)
    cn = urlopen(url)
    totalsize = int(cn.headers['content-length'])
    totalread = 0
    if not outfile:
        ct = b""
    while totalsize > totalread:
        toread = min(totalsize - totalread, blocksize)
        co = cn.read(toread)
        totalread += toread
        if printprogress:
            percent = min(totalread * 1e2 / totalsize, 1e2)
            print("\r  %5.1f%% %*d / %d" % (
                  percent, len(str(totalsize)), totalread, totalsize), end='')
        if outfile:
            outfile.write(co)
        else:
            ct += co
    if printprogress:
        print("")
    if not outfile:
        return ct


def getContentIndex(count):
    # this is a disaster
    # but this will just get longer and longer...
    # i'll figure out a better way to do this later
    content_index = 0
    content_index_string = ""
    content_index_offset = 0
    for i in range(0, count):
        if int(content_index) == 0xFF:
            content_index = 0
            content_index_string += "FF"
            content_index_offset = 0
        content_index += (0x80 / (2 << content_index_offset)) * 2
        content_index_offset += 1
    return content_index_string + format(int(content_index), 'X')

sysbase = "http://nus.cdn.c.shop.nintendowifi.net/ccs/download/" + tid
appbase = "http://ccs.cdn.c.shop.nintendowifi.net/ccs/download/" + tid

base = appbase
if tid[4:8].upper() not in app_categories:
    base = sysbase
    print("- downloading cetk")
    ticket = download(base + "/cetk")
else:
    ticket = binascii.unhexlify(ticket.format(sys.argv[2], tid))

print("- downloading tmd")
tmd = download(base + "/tmd")
print("- reading tmd")
contents = []
count = struct.unpack(">H", tmd[0x1DE:0x1E0])[0]
print("- contents: {}".format(count))
contentsize = 0
for c in range(0, count):
    contents.append(binascii.hexlify(tmd[0xB04 + (0x30 * c):0xB04 + (0x30 * c) + 0x4]).decode('utf-8'))
    contentsize += struct.unpack(">Q", tmd[0xB0C + (0x30 * c):0xB0C + (0x30 * c) + 0x8])[0]
print("- total size: {}".format(contentsize))

with open("{}.cia".format(tid), "wb") as cia:
    tmd_f = tmd[0:0xB04 + (0x30 * c) + 0x30]
    tmdsize = len(tmd_f)
    cia.write(binascii.unhexlify("2020000000000000000A000050030000")
              + struct.pack("<I", tmdsize) + b'\0\0\0\0'
              + struct.pack("<Q", contentsize)
              + binascii.unhexlify(getContentIndex(count)).ljust(0x2020, b'\0')
              + certchain
              + ticket[0:0x350] + (b'\0' * 48)
              + tmd_f.ljust(roundup(tmdsize), b'\0'))
    for c in contents:
        print("- downloading: {}".format(c))
        download(base + "/" + c, True, cia)
