#!/usr/bin/python

import struct, sys

mfts = """
c00004f0
2067334f0
114e7d24f0
26496944f0
26f39174f0
27201fc4f0
2765aff4f0
2871fc04f0
28d28d74f0
2a24b4c4f0
2af62574f0
2b45a984f0
2b7a6b04f0
2bb164f4f0
2bf290f4f0
2c954c44f0
2ca31fb0f0
2ca337f0f0
2d04b384f0
2deb8bc4f0
2f41ddc4f0
2f741304f0
3139d004f0
31d42284f0
3effcbc4f0
40d5e574f0
"""

def vint(a):
    l = len(a)
    v = 0
    for i in range(l):
        v |= ord(a[i]) << (i*8)
    if v & (1<<(8*l-1)):
        v = v - (1<<(8*l))
    return v

def dump_runlist(rl, is_mft):
    vcn = 0
    lcn = 0
    if is_mft:
        print ">", "mft_0x%x.bin" % mft_off
        fd = open("mft_0x%x.bin" % mft_off, "w")
    print rl.encode("hex")
    while rl:
        hdr = ord(rl[0])
        lx = hdr & 15
        ox = hdr >> 4
        if lx == 0:
            break
        dl = vint(rl[1:1+lx])
        do = vint(rl[1+lx:1+lx+ox])
        rl = rl[lx+ox+1:]
        lcn += do
        if is_mft:
            with open(sys.argv[1], "r") as sfd:
                sfd.seek(lcn * cs)
                fd.write(sfd.read(dl * cs))
        print "    vcn=0x%x lcn=0x%x run=0x%x" % (vcn, lcn, dl)
        #print "    (0x%x, 0x%x, 0x%x)," % (vcn, lcn, dl)

        vcn += dl
    if is_mft:
        fd.close()
    print

def dump_standard_info(si):
    cdate, mdate, rdate, adate = struct.unpack("<4Q", si[:32])
    print "    date: %x" % cdate

def dump_name(nm):
    nlen, ntype = struct.unpack("<BB", nm[0x40:0x42])
    print "   %r" % nm[0x42:0x42+nlen*2].decode("utf-16le")

def dump_attr(attr, is_mft):
    atype, alen, fc, nlen, noff, aflags, aid = struct.unpack(
        "<IIBBHHH", attr[:0x10]
    )
    print " type 0x%x len 0x%x fc %d nlen %d noff 0x%x aflags 0x%x aid 0x%x" % (
        atype, alen, fc, nlen, noff, aflags, aid
    )
    if fc == 0:
        clen, coff = struct.unpack("<IH", attr[0x10:0x16])
        if atype == 0x10:
            dump_standard_info(attr[coff:coff+clen])
        elif atype == 0x30:
            dump_name(attr[coff:coff+clen])
    else:
        svcn, evcn, rloff, cunit, attrsz, dsksz, intsz = struct.unpack(
            "<QQHH4xQQQ", attr[0x10:0x40]
        )
        runlist = attr[0x40:]
        dump_runlist(runlist, is_mft and atype == 0x80)

def dump_entry(fr, is_mft=False):
    if fr[:4] != "FILE":
        print "Not an MFT entry"
        return
    seqoff, seqsz, seqno, hard, attr_off, flags, used, alloc, base, next_id, recno = struct.unpack(
        "<4xHH8xHHHHIIQH2xI", fr[:0x30])
    print "seq %d hard %d attr 0x%x flags %04x used %d alloc %d base 0x%x next_id 0x%x recno %d" % (
        seqno, hard, attr_off, flags, used, alloc, base, next_id, recno
        )
    fixup = fr[seqoff:seqoff+seqsz*2]
    fr = fr[:0x1fe] + fixup[2:4] + fr[0x200:0x3fe] + fixup[4:6]
    attrs = fr[attr_off:]
    while attrs:
        if attrs[:4] == "\xff\xff\xff\xff":
            break
        atype, alen = struct.unpack("<II", attrs[:8])
        dump_attr(attrs[:alen], is_mft)
        attrs = attrs[alen:]



fd = open(sys.argv[1], "r")
cs = 4096

for mft_off in [int(i,16) for i in mfts.split()]:
    mft_off -= 0x4f0
    fd.seek(mft_off)
    entries = fd.read(cs)
    print
    print "MFT @ 0x%x" % mft_off
    dump_entry(entries[:1024], is_mft=True)
    dump_entry(entries[1024:2048])
