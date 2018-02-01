#!/usr/bin/env python
#
# Makes a wav file out of owon oscilloscope waveform save file.
# Tested with SDS6062 only.
#
# Used:
# http://bikealive.nl/owon-bin-file-format.html and
# http://bikealive.nl/tl_files/EmbeddedSystems/Test_Measurement/owon/OWON%20Oscilloscope%20PC%20Guidance%20Manual.pdf
#

import sys
from struct import pack, unpack, calcsize

if (len(sys.argv) < 3):
    print "Usage: ", sys.argv[0], " <datafile> <output .wav file>",
    sys.exit(1)

_data_file = sys.argv[1]
_wav_file = sys.argv[2]

fbytes = open(_data_file).read()

model_desc = {
'SPBW01' : 'PDS6062S, PDS6062T, PDS7102T',
'SPBW11' : 'HDS2062M',
'SPBW10' : 'HDS2062M-N',
'SPBV01' : 'PDS5022S, MSO5022',
'SPBV10' : 'HDS1022M-N',
'SPBV11' : 'HDS1022M',
'SPBV12' : 'HDS1021M',
'SPBX01' : 'MSO7102, PDS8102T',
'SPBX10' : 'HDS3102M-N',
'SPBM01' : 'MSO8202, PDS8202T',
'SPBS01' : 'SDS6062',
'SPBS02' : 'SDS7102',
'SPBS03' : 'SDS8202',
'SPBS04' : 'SDS9302',
}

# There is 44 byte thingy in between the magic and popular metadata
# Assuming its exact model and version info. If the date is there it
# would be cool. Its unpacked into _unknown1.

t_fmt = '<3s1s2si44s'
t_start = 0
t_next = t_start + calcsize(t_fmt)

(_magic, _mtype, _mmodelidx, _flen, _unknown1) = unpack(t_fmt, fbytes[t_start:t_next])
# print _magic, _mtype, _mmodelidx, _flen
print 'Model : ', model_desc[_magic + _mtype + _mmodelidx]

t_fmt = '<3sii'
t_start = t_next
t_next = t_start + calcsize(t_fmt)

# Channel meta data header
(_chid, _offtonextch, _memmodel) = unpack(t_fmt, fbytes[t_start:t_next])

_has_deep1 = _offtonextch < 0

# Only for SDS series.
_has_deep = bool (_memmodel & 2)
_is_deep = bool (_memmodel & 1)

print
print 'Channel Id             :', _chid
print 'Next channel offset    :', abs(_offtonextch)
print 'From beginning of file :', abs(_offtonextch) + 54 + 3
print 'Has deep/extended      :', _has_deep1
print 'Deep memory Present    :', _has_deep
print '            Used       :', _is_deep
print

# Channel acquisition spec.

chHs_base = {
    -2: 0.000001,
     -1: 0.000002,
     0: 0.000005,
     1: 0.00001,
     2: 0.000025,
     3: 0.00005,
     4: 0.0001,
     5: 0.00025,
     6: 0.0005,
     7: 0.001,
     8: 0.0025,
     9: 0.005,
     10: 0.01,
     11: 0.025,
     12: 0.05,
     13: 0.1,
     14: 0.25,
     15: 0.5,
     16: 1,
     17: 2.5,
     18: 5,
     19: 10,
     20: 25,
     21: 50,
     22: 100,
     23: 250,
     24: 500,
     25: 1000,
     26: 2500,
     27: 5000,
     28: 10000,
     29: 25000,
     30: 50000,
     31: 100000
     }

chHs = chHs_base

if (_mtype in set(['S','X','W'])):
    chHs.update({
            -1: 0.000002,
             2: 0.00002,
             5: 0.0002,
             8: 0.002,
             11: 0.02,
             14: 0.2,
             17: 2,
             20: 20,
             23: 200,
             26: 2000,
             29: 20000,
             })

if (_mtype == 'V'):
    chHs.update({
            -1: 0.0000025,
             2: 0.000025,
             5: 0.00025,
             8: 0.0025,
             11: 0.025,
             14: 0.25,
             17: 2.5,
             20: 25,
             23: 250,
             26: 2500,
             29: 25000
             })

chVv = {
    0: 0.002,
    1: 0.005,
    2: 0.01,
    3: 0.02,
    4: 0.05,
    5: 0.1,
    6: 0.2,
    7: 0.5,
    8: 1,
    9: 2,
    10: 5,
    11: 10,
    12: 20,
    13: 50,
    14: 100,
    15: 200,
    16: 500,
    17: 1000,
    18: 2000,
    19: 5000,
    20: 10000
    }


t_fmt = '<iiiiiiiifiif'
t_start = t_next
t_next = t_start + calcsize(t_fmt)

(_draw_offs, _screen_points, _sample_size,
 _slow_ltr_size, _tbaseidx, _vzero, _vbaseidx,
 _attenuation, _timegap, _active_samp_freq,
 _active_cycle, _mv_per_unit) = unpack(t_fmt, fbytes[t_start:t_next])


print "Draw Offset            :", _draw_offs
print "Num of screen points   :", _screen_points
print "Sample size            :", _sample_size
print "Slow scan ltr size     :", _slow_ltr_size
print "Timebase index         :", _tbaseidx
print "  Timebase             :", chHs[_tbaseidx], "mS"
print "Zero sample offset vol :", _vzero, "units"
print "Voltage base index     :", _vbaseidx
print "  Voltage base         :", chVv[_vbaseidx], "V"
print "Attenuation            :", pow(10, _attenuation), "X"
print "Time gap (erraneous)   :", _timegap, "uS"
print "Active Sample freq     :", _active_samp_freq, "Hz"
print "Active Cycle           :", _active_cycle, "uS"
print "Voltage/sample level   :", _mv_per_unit, "mV"

t_start = t_next
t_next = t_start + _sample_size

#
# Dump single channel, 8bit MS .wav file.
# Sample rate is 'wired' in - normally ok. Only one cannot try
# resample and play if its audio
#

# To unsigned array
_data = map(lambda x: 0x80+(unpack('<b', x)[0]), fbytes[t_start:t_next])

# KLUDGE, 15 units on screen, timebase is time per unit
# There is nothing in _active_samp_freq.
_sample_rate = 250000

## Wave format
chunk_head_fmt = '<4si'
fmt_subchunk_fmt = '<hhiihh'
wave_chunk = '4s'
data_fmt = ''

## Defaults taken from from another wave file
fmt_head = pack(fmt_subchunk_fmt, 0x1, 0x1, _sample_rate, _sample_rate, 0x1, 0x8)
fmt = pack(chunk_head_fmt, 'fmt ', len(fmt_head)) + fmt_head
data = pack(chunk_head_fmt, 'data', _sample_size) + bytearray(_data)

wave_chunk = 'WAVE' + fmt + data
riff_chunk = pack(chunk_head_fmt, 'RIFF', len(wave_chunk)) + wave_chunk

f = open (_wav_file, "w")
f.write(riff_chunk)
f.close()
