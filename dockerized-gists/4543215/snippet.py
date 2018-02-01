#!/usr/bin/env python

# Copyright (c) Sabin Iacob <iacobs@gmail.com>.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the University nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

__doc__ = """
Usage:

import dvm1200
import serial

port = serial.Serial('/dev/ttyUSB0') # Linux; other operating systems will be 
                                     # different

while True:
    line = dvm1200.read_data(port)
    data = dvm1200.decode(line)

    print data['value'], data['unit'], ', '.join(data['unit_extra'])', '.join(data['flags'])


Gory details:

The multimeter is as dumb as they come when it comes to PC interfacing,
and makes a screen dump to USB (over an IR link) instead of providing proper
ASCII data. The original software is Windows only and doesn't work in Wine.

The output consists of 14 byte packets that look like this when converted to 
hex:

1b 27 3d 4d 5b 65 7b 87 9e a0 b0 c0 d4 e0

The first 4 bits can be discarded, leaving us with

b 7 d d b 5 b 7 e 0 0 0 4 0

Further, these can be grouped like

b 7d db 5b 7e 00 04 0

These encode various things on the screen; in order of appearance:
 * left side flags (AC, DC, PC-Link, AUTO)
 * first digit
 * second digit
 * third digit
 * fourth digit
 * mostly scaling information (nano, micro, milli, etc.), but also diode, beep
 * mostly units (V, A, F, Hz), but also REL, H(old)
 * top flags: MIN, MAX, but also deg. C

The last half byte looks like [MIN, <no idea>, deg.C, MAX]. The digits use a 
non-standard layout (check decode_digit), but are basically seven segment 
displays; the "decimal point" bit of the leftmost digit controls the sign display.
"""

def read_data(port):
    data = port.read(14)
    data = [c.encode('hex')[1] for c in data]

    ret = [
        data[0],             # left indicators
        data[1] + data[2],   # digit 1
        data[3] + data[4],   # digit 2
        data[5] + data[6],   # digit 3
        data[7] + data[8],   # digit 4
        data[9] + data[10],  # scale
        data[11] + data[12], # units
        data[13],            # top indicators
    ]

    return ret

def decode_digit(n):
    """
              d
             ---
          c | g | h
      --     ---
      a   b |   | f
      .      ---
              e
    """
    trans_tbl = {
        0b00000101: 1,
        0b01011011: 2,
        0b00011111: 3,
        0b00100111: 4,
        0b00111110: 5,
        0b01111110: 6,
        0b00010101: 7,
        0b01111111: 8,
        0b00111111: 9,
        0b01111101: 0,
        0b01101000: 'L',
    }

    if isinstance(n, basestring):
        n = int(n, 16)

    has_dot = bool(n & 128)
    n &= ~128

    return trans_tbl.get(n), has_dot

def decode_flags(n):
    if isinstance(n, basestring):
        n = int(n, 16)

    names = ['AC', 'DC', 'AUTO', 'PC']
    flags = [bool(n & (1 << (3 - i))) for i in range(4)]

    return [names[i] for i in range(4) if flags[i]]

def decode_units(n1, n2):
    if isinstance(n1, basestring):
        n1 = int(n1, 16)

    if isinstance(n2, basestring):
        n2 = int(n2, 16)

    scale = ['u', 'n', 'k', 'Diode', 'm', '%', 'M', 'Beep']
    unit = ['F', 'Ohm', 'Relative', 'Hold', 'A', 'V', 'Hz', '?']

    fscale = [bool(n1 & (1 << (7 - i))) for i in range(8)]
    funit = [bool(n2 & (1 << (7 - i))) for i in range(8)]

    rscale = [scale[i] for i in range(8) if fscale[i]]
    runit = [unit[i] for i in range(8) if funit[i]]

    scales = set(['u', 'n', 'k', 'm', 'M'])
    units = set(['F', 'Ohm', 'A', 'V', 'Hz'])

    scale = ''
    unit = ''
    try:
        unit = units.intersection(runit).pop()
        scale = scales.intersection(rscale).pop()
    except KeyError:
        pass

    return [scale + unit] + list(set(rscale) - scales) + list(set(runit) - units)

def decode_value(line):
    d1, d2, d3, d4 = map(decode_digit, line[1:5])

    sign = 1
    mult = 1

    if d1[1]:
        sign = -1
    if d2[1]:
        mult = 0.001
    elif d3[1]:
        mult = 0.01
    elif d4[1]:
        mult = 0.1

    if d3[0] == 'L':
        return 0

    ret = d4[0] + 10 * d3[0] + 100 * d2[0] + 1000 * d1[0]

    return sign * mult * ret

def decode(line):
    flags = decode_flags(line[0])
    units = decode_units(line[5], line[6])

    return {
        'value': decode_value(line),
        'flags': flags,
        'unit': units[0],
        'unit_extra': units[1:],
    }

if __name__ == '__main__':
    import serial

    port = serial.Serial('/dev/ttyUSB0')
    try:
        while True:
            line = read_data(port)
            data = decode(line)

            print data['value'], data['unit'], ', '.join(data['unit_extra']), \
                  ', '.join(data['flags'])

    except KeyboardInterrupt:
        pass
