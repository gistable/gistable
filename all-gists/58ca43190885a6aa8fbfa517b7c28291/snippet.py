"""
:|
- Email provider doesn't allow me to send certain file types.
- I have python installed on all my machines.
- Inflates the file size by ~4.5X, still remains under 25M for me.
"""

from __future__ import print_function
import sys

inpfile = sys.argv[1]
data_ = open(inpfile, "rb").read()
byte_array_ = bytearray(data_)
print("byte_array_ = bytearray([" + ", ".join([str(b) for b in byte_array_]) + "])")
print("open('" + inpfile + "', 'wb').write(byte_array_)")

#~~ PS: Improvements and suggestions are welcome! ~~#
