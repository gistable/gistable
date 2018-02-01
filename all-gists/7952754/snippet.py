import struct
from itertools import izip_longest

def grouper(n, iterable, fillvalue=None):
  "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx... From stackoverflow"
  args = [iter(iterable)] * n
  return izip_longest(fillvalue=fillvalue, *args)

# Extract data from data_file which is a "binary string". Returns it in the format (Data[31 downto 8], Data[7 downto 0])
# which is technically data, ADC channel
data_file = "\x81\x82\x83\x01\x84\x85\x86\x02\x21\x30\xf1\x01"
[(h>>8, h&0xff) for i in grouper(4, data_file) for h in struct.unpack("!I",''.join(i))]

# Better solution
[struct.unpack("!IB",'\x00' + (''.join(i))) for i in grouper(4, data_file)]