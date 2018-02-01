"""
This script writes the VDSO to the file linux-gate.dso.1 .
Use `objdump -d linux-gate.dso.1` to examine it.
You might also want to play around more with the other objdump options and
the readelf tool :)

LICENSE: MIT License ( http://www.opensource.org/licenses/mit-license.php )
"""
from __future__ import with_statement
import os
import re

## regex pattern for finding out the memory address range from the output line
pattern = re.compile(r'[\w\d]+-[\w\d]+')
with open('/proc/self/maps', 'r') as file:
    for line in file:
        line = line.rstrip()
        if '[vdso]' in line:
            addr_range = pattern.findall(line)[0]
            start_addr, end_addr = [int(addr, 16) 
                                    for addr in addr_range.split('-')]
            break

fd = os.open('/proc/self/mem', os.O_RDONLY)
os.lseek(fd, start_addr, os.SEEK_SET)
buf = os.read(fd, (end_addr-start_addr))

with open('linux-gate.dso.1', 'w') as file:
    file.write(buf)
    file.close()
os.close(fd)