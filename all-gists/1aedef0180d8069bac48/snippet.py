#!env python3
#
# Copyright (c) 2015 Jon Szymaniak <jon.szymaniak@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software. 
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
################################################################################

import sys

if len(sys.argv) < 3 or len(sys.argv) > 5:
    print('')
    print('regfield: A simple register field calculator')
    print('Usage:', sys.argv[0], '<register value> <MSB> [LSB] [write value]');
    print('')
    print('Examples:')
    print('')
    print(' Read [6:3] from a register with value 0xbcf3:')
    print('   $', sys.argv[0], '0xbcf3 6 3')
    print('   [6:3]     14     0xe     0b1110')
    print('')
    print(' Write 0xb1 to [33:12], for a current value of 0x11f3d:')
    print('   $', sys.argv[0], '0x11f3d 33 12 0x1bd')
    print('   0x1bdf3d')
    print('')

    sys.exit(1)

try:
    regval = int(sys.argv[1], 0)
    if regval < 0 or regval >= (1 << 64):
        raise ValueError
except ValueError:
    print('Invalid register value:', sys.argv[1])
    sys.exit(1)

try:
    msb = int(sys.argv[2], 0)
    if msb < 0 or msb >= 64:
        print('This script only supports MSB values of [0, 63]')
        sys.exit(1)
except ValueError:
    print('Invalid MSB value:', sys.argv[2])
    sys.exit(1)

if len(sys.argv) >= 4:
    mode = 'read';
    try:
        lsb = int(sys.argv[3], 0)
        if lsb < 0 or lsb >= 64:
            print('This script only supports LSB values of [0, 63]')
            sys.exit(1)
        elif (lsb > msb):
            print('This script currently only supports big-endian bit ordering. (MSB > LSB)')
            sys.exit(1)
    except ValueError:
        print('Invalid LSB value:', sys.argv[3])
        sys.exit(1)

    if len(sys.argv) >= 5:
        mode = 'write'
        try:
            write_val = int(sys.argv[4], 0);
        except ValueError:
            print('Invalid write value:', sys.argv[4])
            sys.exit(1)

else:
    mode = 'read'
    lsb = msb

field_width = msb - lsb + 1
mask        = (1 << field_width) - 1

if mode == 'read':
    regval_shift    = regval >> lsb
    regval_masked   = regval_shift & mask

    print('[' + str(msb) + ':' + str(lsb) + ']    ',
            regval_masked, '   ',
            hex(regval_masked), '   ',
            bin(regval_masked))

elif mode == 'write':
    if (write_val > mask):
        print('Error: Write value is larger than field width.')
        sys.exit(1)

    mask = mask << lsb

    regval &= ~mask;
    regval |= (write_val << lsb)

    print(hex(regval))

else:
    print('Bug: Invalid mode encountered')
    sys.exit(1)
