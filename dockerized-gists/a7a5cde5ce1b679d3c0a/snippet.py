###########################################################################
# Rotating bits (tested with Python 2.7)
 
from __future__ import print_function   # PEP 3105
 
# max bits > 0 == width of the value in bits (e.g., int_16 -> 16)
 
# Rotate left: 0b1001 --> 0b0011
rol = lambda val, r_bits, max_bits: \
    (val << r_bits%max_bits) & (2**max_bits-1) | \
    ((val & (2**max_bits-1)) >> (max_bits-(r_bits%max_bits)))
 
# Rotate right: 0b1001 --> 0b1100
ror = lambda val, r_bits, max_bits: \
    ((val & (2**max_bits-1)) >> r_bits%max_bits) | \
    (val << (max_bits-(r_bits%max_bits)) & (2**max_bits-1))
 
max_bits = 16  # For fun, try 2, 17 or other arbitrary (positive!) values
 
print()
for i in xrange(0, max_bits*2-1):
    value = 0xC000
    newval = rol(value, i, max_bits)
    print("0x%08x << 0x%02x --> 0x%08x" % (value, i, newval))
 
print()
for i in xrange(0, max_bits*2-1):
    value = 0x0003
    newval = ror(value, i, max_bits)
    print("0x%08x >> 0x%02x --> 0x%08x" % (value, i, newval))
 
###########################################################################